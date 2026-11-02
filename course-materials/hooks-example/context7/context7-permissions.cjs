const fs = require('node:fs');

const event = JSON.parse(fs.readFileSync(0, 'utf8'));
const toolName = event.toolName ?? event.tool_name;
const shellTools = new Set(['powershell', 'bash', 'Bash', 'run_in_terminal']);

if (typeof toolName !== 'string') {
  throw new Error('Expected a hook event with toolName or tool_name.');
}

let output = {};
if (shellTools.has(toolName)) {
  const rawArgs = event.toolArgs ?? event.tool_input;
  const args = typeof rawArgs === 'string' ? JSON.parse(rawArgs) : rawArgs;
  if (typeof args?.command !== 'string') {
    throw new Error('Expected a shell command string.');
  }

  // Approve the entire invocation, never a prefix or an interpolated query.
  // npm batch shims may cross into cmd.exe even from PowerShell. Keep both
  // quoted forms free of batch metacharacters and embedded double quotes.
  // PowerShell also recognizes smart quotes as delimiters; reject controls.
  const quotedArgument = /(?:"[^"$`\\&|<>^%!\u2018-\u201e\x00-\x1f\x7f]+"|'[^'"&|<>^%!\u2018-\u201e\x00-\x1f\x7f]+')/.source;
  const libraryId = /\/[A-Za-z0-9_.@+-]+(?:\/[A-Za-z0-9_.@+-]+)+/.source;
  const context7Command = new RegExp(
    `^[ \t]*npx(?:\\.cmd)?[ \t]+(?:(?:--yes|-y)[ \t]+)?ctx7@latest[ \t]+` +
    `(?:library[ \t]+${quotedArgument}|docs[ \t]+${libraryId})[ \t]+${quotedArgument}[ \t]*$`,
  );
  const decision = context7Command.test(args.command)
    ? 'allow'
    : /\bnpx(?:\.cmd|\.exe)?\b/i.test(args.command) ? 'ask' : undefined;

  if (decision) {
    const reason = decision === 'allow'
      ? 'Project policy allows this standalone Context7 documentation query.'
      : 'This npx invocation requires user approval. Only simple standalone npx ctx7@latest library "name" "question" or docs /owner/library "question" queries, with optional --yes or -y, are automatically approved.';
    output = {
      permissionDecision: decision,
      permissionDecisionReason: reason,
      // Copilot CLI uses the top-level fields; VS Code Local uses this envelope.
      hookSpecificOutput: {
        hookEventName: 'PreToolUse',
        permissionDecision: decision,
        permissionDecisionReason: reason,
      },
    };
  }
}

process.stdout.write(JSON.stringify(output));
