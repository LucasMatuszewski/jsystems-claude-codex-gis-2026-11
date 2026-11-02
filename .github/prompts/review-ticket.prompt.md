---
agent: 'agent'
description: 'Review one bounded feature diff against its approved requirement and actual tests'
---

Identify the actual application checkout, the approved criterion or ticket, and the current diff. Read the relevant PRD/ADR sections, applicable instructions, implementation and existing tests. Ask only for consequential missing sources; do not assume a particular language, practice track or docs/problem-brief.md exists. Teaching examples in course-materials are not requirements.

Do not edit files. Report: (1) mismatches with the approved criterion, (2) observed test results or the actual project command needed to reproduce them, (3) unrelated changes, skipped tests or weakened assertions, (4) concrete risks with evidence, and (5) an evidence-based recommendation to accept, revise or reject. Cite files and lines. Distinguish source inspection, executed tests, startup and manual runtime checks; never claim unperformed verification. Use synthetic data and follow the repository's permission/data policy. This recommendation is not permission to commit, publish or merge.
