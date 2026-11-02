---
name: test-evidence
description: Use when asked to assess the evidence for one feature's tests against its approved requirement and current diff, without editing implementation or tests.
---

# Evidence for one feature's tests

Identify the actual application checkout, the approved criterion, the current diff and the existing test commands. Ask only for consequential missing inputs. Teaching examples are not requirements.

Read the relevant implementation and tests. Check observable success, boundary and failure behavior; note mocks that replace the behavior under test, weakened assertions, skips or unrelated changes. Follow the repository's data and permission policy. Do not read credentials, personal records or private customer tickets.

Run only already authorized checks in a safe environment with synthetic data. If the command cannot run, report that prerequisite and an exact reproduction command; do not invent a result or install a new stack merely to complete the report.

Return a compact table: criterion, test/evidence, observed result and gap. Distinguish test discovery/execution, startup and manual runtime verification. Cite concrete files and lines for findings; absence of a test is different from a reproduced production defect.

Do not edit production or tests, launch other agents, commit, publish or approve a merge. Return an evidence-based recommendation for the human/coordinator. For implementation, use a separately assigned bounded task rather than broadening this assessment.
