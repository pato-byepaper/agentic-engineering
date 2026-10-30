# Knowledge Base

Repository architecture invariants and domain context.

## System Topology
- Multi-agent autonomous software engineering pipeline.
- Roles: Manager, Tech Lead, Data Engineer, Backend Developer, Frontend Developer, Committer, Tester, Code Reviewer, Planner, Doc Maintainer.

## Strict Invariants
- Zero developer self-testing: only Tester creates and runs tests.
- Mandatory at least 3 stacked PRs for full-stack features (Data -> Backend -> Frontend).
- Mandatory at least 1 commit per task via Committer.
- Zero emojis and zero AI co-author tags.
- Large context managed via regex-based RAG service and relationship graph service.
