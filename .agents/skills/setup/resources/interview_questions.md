# Project Onboarding & Architecture Alignment Interview

After scanning the codebase and generating the baseline `context/` files for each agent, the agent running the `setup` skill must send a couple of thoughtful questions to the user to align on domain, stack choices, and architecture rationale.

---

## Question Set 1: Project Purpose & Domain
> "1. **Project & Domain**: What is the primary purpose of this project, who are the core users, and what business/technical problem does it solve?"

## Question Set 2: Architecture & Stack Rationale
> "2. **Stack & Architectural Decisions**: I noticed the detected stack includes [list detected technologies]. Why was this particular architecture/stack chosen, and are there specific patterns (e.g. Clean Architecture, Event-Driven, Server Actions, microservices) that all agents must strictly follow?"

## Question Set 3: Data & Invariants
> "3. **Data & Security**: How is data managed (e.g. multi-tenant isolation, Row Level Security, caching layers), and are there strict database migration rules we should enforce?"

## Question Set 4: Critical Invariants & Non-Negotiables
> "4. **Verification & Web Performance**: What are the critical tests/benchmarks that must never fail, and are there special performance constraints (e.g., Google Core Web Vitals targets, max API latency)?"

---

## Post-Interview Action
Once the user replies with their answers:
1. Update each agent's `context/*.md` file with the domain insights, specific patterns, and non-negotiables.
2. Confirm to the user that the entire team (`manager`, `tech-lead`, `data-engineer`, `backend-developer`, `frontend-developer`, `tester`, `git-publisher`) is now fully customized and ready for autonomous execution on the codebase.
