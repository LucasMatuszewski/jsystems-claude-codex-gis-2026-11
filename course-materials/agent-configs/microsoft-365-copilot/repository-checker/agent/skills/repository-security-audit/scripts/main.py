#!/usr/bin/env python3
import argparse, json, os, re
from pathlib import Path
RULES = [
("agent-override","high",r"ignore (all |any )?(previous|prior|system|developer) instructions|system prompt|jailbreak|developer mode|bypass (safety|guardrails)"),
("secret-exfil","critical",r"(upload|send|post|exfiltrat).{0,80}(token|secret|password|credential|\.env|ssh|api.?key)"),
("dynamic-exec","high",r"\b(eval|exec)\s*\(|Runtime\.getRuntime\(\)\.exec|ProcessBuilder\s*\(|child_process\.(exec|spawn)|subprocess\.(run|Popen)|os\.system\s*\("),
("download-exec","critical",r"(curl|wget|Invoke-WebRequest).{0,160}(\||&&|;).{0,40}(sh|bash|python|powershell)|download.{0,80}(execute|run)"),
("telemetry","medium",r"telemetry|analytics|tracking|sentry|segment|mixpanel|amplitude|posthog|crashlytics|applicationinsights"),
("credential-access","high",r"(AWS_SECRET_ACCESS_KEY|GITHUB_TOKEN|AZURE_CLIENT_SECRET|\.ssh/|id_rsa|keychain|credential manager)"),
("unsafe-network","medium",r"http://|verify\s*=\s*False|trustAll|HostnameVerifier|InsecureSkipVerify"),
("persistence-hook","high",r"postinstall|preinstall|prepare\s*[:=]|\.git/hooks|cron(tab)?|systemd|LaunchAgents|Run\\\\"),
("obfuscation","medium",r"fromCharCode|atob\s*\(|base64\.b64decode|Base64\.getDecoder|marshal\.loads|pickle\.loads"),
("mcp-risk","high",r"mcp.{0,80}(shell|command|filesystem|write|delete|execute)|tool.{0,80}(shell|command|exec)"),
("java-risk","high",r"ObjectInputStream|InitialContext|JNDI|Class\.forName|System\.loadLibrary|DocumentBuilderFactory|SAXParserFactory")]
SKIP={".git","node_modules","vendor","dist","build","target",".venv","venv"}
# Excerpts go into a report file, so credential values are masked before they are stored.
REDACT=[(re.compile(r"(\w+://)[^/\s:@]+:[^/\s@]+@"),r"\1[REDACTED]@"),
(re.compile(r"\b(Bearer|Basic|Digest)\s+[^\s\"',;)}]+",re.I),r"\1 [REDACTED]"),
(re.compile(r"((?:token|secret|passw(?:or)?d|pwd|api.?key|access.?key|private.?key|credential)\w*[\"']?\s*[:=]\s*[\"']?)[^\s\"',;]+",re.I),r"\1[REDACTED]"),
(re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*"),"[REDACTED PRIVATE KEY]"),
(re.compile(r"\b(gh[pousr]_|github_pat_|xox[abprs]-|sk-|AKIA)[\w-]+"),"[REDACTED]"),
(re.compile(r"(?=[\w+/=-]*\d)(?=[\w+/=-]*[A-Za-z])[\w+/=-]{16,}"),"[REDACTED]")]
def redact(line):
 for pat,rep in REDACT: line=pat.sub(rep,line)
 return line
def scan(root,max_bytes):
 out=[]; skipped=[]
 # os.walk does not follow directory symlinks; SKIP applies only below the scan root.
 for d,dirs,files in os.walk(root):
  base=Path(d)
  for x in sorted(dirs):
   if x in SKIP or (base/x).is_symlink():
    dirs.remove(x); skipped.append({"path":str((base/x).relative_to(root)),"reason":"symlink" if (base/x).is_symlink() else "excluded"})
  dirs.sort()
  for f in sorted(files):
   p=base/f; rel=str(p.relative_to(root))
   try:
    if p.is_symlink(): skipped.append({"path":rel,"reason":"symlink"}); continue
    if not p.is_file(): skipped.append({"path":rel,"reason":"not a regular file"}); continue
    if p.stat().st_size>max_bytes: skipped.append({"path":rel,"reason":"size"}); continue
    raw=p.read_bytes()
    if b"\0" in raw[:4096]: skipped.append({"path":rel,"reason":"binary"}); continue
    text=raw.decode("utf-8","replace")
    for n,line in enumerate(text.splitlines(),1):
     for rid,sev,pat in RULES:
      if re.search(pat,line,re.I): out.append({"rule":rid,"severity":sev,"path":rel,"line":n,"excerpt":redact(line.strip())[:300]})
   except Exception as e: skipped.append({"path":rel,"reason":type(e).__name__})
 return out,skipped
if __name__=="__main__":
 ap=argparse.ArgumentParser(); ap.add_argument("path"); ap.add_argument("--output",default="repository-audit.json"); ap.add_argument("--max-bytes",type=int,default=2_000_000); a=ap.parse_args()
 root=Path(a.path).resolve()
 if not root.is_dir(): ap.error(f"not a directory: {root}")
 # The scanned repository is untrusted: a report path inside it may be a planted symlink, and a report there would be rescanned.
 out=Path(os.path.abspath(a.output))
 if out.is_symlink() or out.is_relative_to(root) or out.resolve().is_relative_to(root): ap.error(f"write the report outside the scanned repository: {out}")
 findings,skipped=scan(root,a.max_bytes); data={"findings":findings,"skipped":skipped,"counts":{s:sum(x["severity"]==s for x in findings) for s in ["critical","high","medium","low"]}}
 out.write_text(json.dumps(data,indent=2),encoding="utf-8"); print(json.dumps(data["counts"]))
