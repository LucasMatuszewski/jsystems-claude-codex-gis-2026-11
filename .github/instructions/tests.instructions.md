---
applyTo: '**/tests/**,**/test/**,**/*.test.*,**/*.spec.*,**/test_*.py,**/*Test.*,**/*Tests.*,**/*_test.*'
description: 'Behavior-focused test evidence for the selected application'
---

Use the selected application's approved behavior and actual test runner. Assert observable results, state changes and errors; avoid source-layout checks or mocks that replace the behavior under test. Use synthetic data, and follow the repository's policy for obtaining safe real response captures before creating API/database mocks.

A new behavior or bug fix needs a reproducing expected failure before implementation. For characterization of existing behavior, first record a passing baseline. Report an already-passing criterion as existing coverage rather than inventing a failure. Do not delete or weaken assertions, skip tests or tune fixtures just to obtain green output.

For an explicitly test-only assignment, keep changes inside the assigned test files. For an authorized feature or bug fix, follow the assigned production-and-test scope and the repository's TDD workflow; matching a test-file glob does not prohibit the authorized implementation. Report discovery, executed tests, skips and failures separately from application startup or manual QA. Changing expected behavior needs support from the approved requirement; unexplained production defects go back to the coordinator.
