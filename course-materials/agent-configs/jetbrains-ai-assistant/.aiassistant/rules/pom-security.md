---
apply: by file patterns
patterns: pom.xml
---

Research dependencies before you install them.
Make sure they are safe to use, do not have security or performance issues, etc.
In case of very simple dependencies or if we use only a small part of a dependency, suggest to implement the code in our codebase.
Remember that every dependency is a potential risk, and it's usually better to implement something in our own codebase.