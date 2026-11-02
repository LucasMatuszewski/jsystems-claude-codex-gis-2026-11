# Windows twin of block-secrets.sh for Copilot CLI (the "powershell" hook key).
# Blocks any tool call whose input mentions .env, secrets/, a private SSH key
# or a .pem file. .env.example, .env.sample and .env.template stay allowed.

$payload = [Console]::In.ReadToEnd()
$checked = $payload -replace '\.env\.(example|sample|template)', ''
$pattern = '(^|[^A-Za-z0-9_-])\.env([^A-Za-z0-9_-]|\.[A-Za-z0-9_-]+|$)|(^|[^A-Za-z0-9_.-])secrets[/\\]|id_(rsa|ed25519|ecdsa)|\.pem([^A-Za-z0-9]|$)'

if ($checked -match $pattern) {
    $reason = 'Blocked by block-secrets hook: this call touches a secrets file (.env, secrets/, SSH key or .pem). Use .env.example or ask the user.'
    [Console]::Out.WriteLine((@{ permissionDecision = 'deny'; permissionDecisionReason = $reason } | ConvertTo-Json -Compress))
    [Console]::Error.WriteLine($reason)
    exit 2
}
exit 0
