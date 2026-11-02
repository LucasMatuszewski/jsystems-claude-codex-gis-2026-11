const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const { test } = require('node:test');

const script = path.join(__dirname, 'context7-permissions.cjs');
const example = 'npx --yes ctx7@latest docs /vercel/ai "Current AI SDK APIs for generateText structured output using Output.object and Zod, plus streamText returned as a UI message stream for a Next.js App Router Route Handler; use current version terminology."';

function run(event) {
  const result = spawnSync(process.execPath, [script], {
    input: typeof event === 'string' ? event : JSON.stringify(event),
    encoding: 'utf8',
  });
  assert.equal(result.status, 0, result.stderr);
  return JSON.parse(result.stdout);
}

const formats = {
  cli: (command) => ({ toolName: 'powershell', toolArgs: { command } }),
  vscode: (command) => ({ tool_name: 'run_in_terminal', tool_input: { command } }),
  compatible: (command) => ({ tool_name: 'Bash', tool_input: { command } }),
};

const allowed = [
  example,
  'npx --yes ctx7@latest docs /facebook/react "Explain hooks"',
  "npx -y ctx7@latest docs /vercel/next.js/v16 'Explain route handlers'",
  'npx.cmd --yes ctx7@latest docs /mongodb/docs "Pytanie o indeksy"',
  '  npx --yes ctx7@latest docs /org/any-library "Explain API examples and alternatives"  ',
  "npx --yes ctx7@latest docs /org/library 'Explain $variables and `backticks`'",
];

// These cases catch an allowlist that omits resolution or requires --yes.
allowed.push(
  'npx ctx7@latest library "Next.js" "Find App Router documentation"',
  "npx --yes ctx7@latest library 'Customer.io' 'Find API documentation'",
  'npx -y ctx7@latest library "Three.js" "Find animation documentation"',
  'npx.cmd ctx7@latest library "React" "Find hooks documentation"',
  'npx.cmd --yes ctx7@latest library "React" "Find hooks documentation"',
  "npx.cmd -y ctx7@latest library 'React' 'Find hooks documentation'",
  'npx ctx7@latest docs /facebook/react "Explain hooks"',
  "npx.cmd ctx7@latest docs /vercel/next.js/v16 'Explain route handlers'",
  'npx.cmd -y ctx7@latest docs /org/library "Explain API"',
  'npx ctx7@latest library "Przykładowa biblioteka" "Znajdź opis właściwości"',
  'npx.cmd ctx7@latest docs /org/library "Wyjaśnij żądania i źródła błędów"',
);

const requiresApproval = [
  'npx playwright test',
  'npx create-next-app@latest demo',
  'npx --yes other-package "question"',
  'npx --yes ctx7@latest library react',
  'npx --yes ctx7@latest docs /vercel/ai',
  'npx --yes ctx7@latest docs /vercel/ai ""',
  'npx --yes ctx7@latest docs /vercel/ai question',
  'npx --yes ctx7@latest docs /vercel/ai "question" --extra',
  'npx --yes ctx7@latest docs /vercel/ai "question"; Write-Output unsafe',
  'npx --yes ctx7@latest docs /vercel/ai "question" && echo unsafe',
  'npx --yes ctx7@latest docs /vercel/ai "question" | another-command',
  'npx --yes ctx7@latest docs /vercel/ai "question" > output.txt',
  'npx --yes ctx7@latest docs /vercel/ai "$(Write-Output unsafe)"',
  'npx --yes ctx7@latest docs /vercel/ai "`whoami`"',
  'npx --yes ctx7@latest docs /vercel/ai "$env:SECRET"',
  'npx --package other-package ctx7 docs /vercel/ai "question"',
  'npx --yes ctx7@other-version docs /vercel/ai "question"',
  'npx --yes ctx7@latest docs /vercel/ai "question"\nWrite-Output unsafe',
  'cmd /c npx --yes other-package',
  'powershell -Command "npx --yes other-package"',
  '& "C:\\tools\\npx.cmd" --yes other-package',
];

// These cases catch argument broadening, shell expansion and newline bypasses.
requiresApproval.push(
  'npx ctx7@latest library React "Find hooks documentation"',
  'npx ctx7@latest library "React" documentation',
  'npx ctx7@latest library "" "Find hooks documentation"',
  'npx ctx7@latest library "React" ""',
  'npx ctx7@latest library "React"',
  'npx ctx7@latest library "React" "Find docs" --extra',
  'npx ctx7@latest library "React" "Find docs"; echo unsafe',
  'npx ctx7@latest library "React" "Find docs" && echo unsafe',
  'npx ctx7@latest library "React" "Find docs" | echo unsafe',
  'npx ctx7@latest library "React" "Find docs" > output.txt',
  'npx ctx7@latest library "$(whoami)" "Find docs"',
  'npx ctx7@latest library "React" "$env:SECRET"',
  'npx ctx7@latest library "React" "`whoami`"',
  'npx --yes -y ctx7@latest docs /org/library "Find docs"',
  'npx --quiet ctx7@latest library "React" "Find docs"',
  'npx ctx7@latest docs /org "Find docs"',
  'npx ctx7@latest docs /org/library "Find docs" extra',
  'npx ctx7@latest library "React" "Find\ndocs"',
  'npx ctx7@latest library "React" "Find docs"\necho unsafe',
  'npx --yes ctx7@latest docs /org/library "Find docs"\n',
  'npx --yes ctx7@latest docs /org/library "Find docs"\r',
  'npx --yes ctx7@latest docs /org/library "Find docs"\r\n',
);


// PowerShell may hand a Windows npm batch shim to cmd.exe. Even quoted
// arguments must not autoapprove metacharacters or embedded double quotes.
for (const executable of ['npx', 'npx.cmd']) {
  requiresApproval.push(
    `${executable} ctx7@latest library 'React" & echo UNSAFE & rem "' 'Find docs'`,
    `${executable} ctx7@latest library "React' &echo UNSAFE& rem '" "Find docs"`,
    `${executable} ctx7@latest library "React" "Find&docs"`,
    `${executable} ctx7@latest docs /org/library "Find|docs"`,
    `${executable} ctx7@latest docs /org/library "%SYNTHETIC_TOKEN%"`,
    `${executable} ctx7@latest docs /org/library "!SYNTHETIC_TOKEN!"`,
    `${executable} ctx7@latest docs /org/library "Find^docs"`,
    `${executable} ctx7@latest docs /org/library "Find>docs"`,
    `${executable} ctx7@latest docs /org/library 'Find<docs'`,
    `${executable} ctx7@latest docs /org/library 'Explain "quoted" text'`,
  );
}


// PowerShell treats smart quotation marks as delimiters. Neither quote form
// may hide them or control characters inside an otherwise allowed argument.
for (const executable of ['npx', 'npx.cmd']) {
  for (const quote of ["'", '"']) {
    for (const character of ['‘', '’', '“', '”', '\0', '\t', '\x1b', '\x7f']) {
      requiresApproval.push(
        `${executable} ctx7@latest docs /org/library ${quote}Find docs${character}; echo UNSAFE; # ${quote}`,
      );
    }
  }
}

for (const [format, event] of Object.entries(formats)) {
  for (const [index, command] of allowed.entries()) {
    test(`${format}: allows standalone Context7 query ${index + 1}`, () => {
      const result = run(event(command));
      assert.equal(result.permissionDecision, 'allow');
      assert.equal(result.hookSpecificOutput.permissionDecision, 'allow');
      assert.equal(result.hookSpecificOutput.hookEventName, 'PreToolUse');
    });
  }
  for (const [index, command] of requiresApproval.entries()) {
    test(`${format}: asks for approval for other npx calls ${index + 1}`, () => {
      const result = run(event(command));
      assert.equal(result.permissionDecision, 'ask');
      assert.equal(result.hookSpecificOutput.permissionDecision, 'ask');
      assert.ok(result.permissionDecisionReason);
    });
  }
  test(`${format}: leaves unrelated shell permissions unchanged`, () => {
    assert.deepEqual(run(event('git status --short')), {});
  });
}

test('leaves non-shell tools unchanged', () => {
  assert.deepEqual(run({ toolName: 'view', toolArgs: { path: 'npx.txt' } }), {});
});

test('accepts CLI JSON-string arguments', () => {
  assert.equal(run({
    toolName: 'powershell',
    toolArgs: JSON.stringify({ command: example }),
  }).permissionDecision, 'allow');
});

test('reports malformed shell input instead of granting permission', () => {
  const result = spawnSync(process.execPath, [script], {
    input: JSON.stringify({ toolName: 'powershell', toolArgs: {} }),
    encoding: 'utf8',
  });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /Expected a shell command string/);
});
