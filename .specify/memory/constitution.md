<!--
══════════════════════════════════════════════════════════════════════════════
SYNC IMPACT REPORT
══════════════════════════════════════════════════════════════════════════════
Version Change: N/A → 1.0.0 (Initial Ratification)

Modified Principles: N/A (first version)

Added Sections:
  - Core Principles (5 principles: Spec First, Agent Discipline, Incremental
    Evolution, Test-Backed Progress, Traceability)
  - Authorized Sub-Agents (8 agents defined)
  - Phase Governance (5 phases with completion criteria)
  - Error Handling Requirements
  - Output Requirements
  - Final Authority
  - Governance (amendment procedure, versioning, compliance)

Removed Sections: N/A (first version)

Templates Validation:
  ✅ .specify/templates/plan-template.md - Constitution Check section aligns
  ✅ .specify/templates/spec-template.md - Requirements format aligns with SPEC FIRST
  ✅ .specify/templates/tasks-template.md - Phase structure aligns with principles

Follow-up TODOs: None
══════════════════════════════════════════════════════════════════════════════
-->

# Hackathon II – The Evolution of Todo: Constitution

**Mission**: Ensure the Todo application is built, evolved, and deployed across all phases using strict Spec-Driven Development principles, agent specialization, and cloud-native best practices — without skipping validation, testing, or architectural discipline.

## Core Principles

### I. Spec First (NON-NEGOTIABLE)

No code, configuration, or deployment is allowed without an approved specification.

- Every feature MUST begin with a written spec in `/specs/<feature>/spec.md`
- Specs MUST define: inputs, outputs, edge cases, and failure behavior
- Ambiguity MUST trigger refinement, not assumptions
- Code changes MUST reference their originating spec requirement

**Rationale**: Specifications prevent scope creep, ensure shared understanding, and provide the foundation for testable acceptance criteria.

### II. Agent Discipline

Each sub-agent may only act within its defined role and skills.

- Agents MUST NOT override or perform actions assigned to other agents
- Cross-agent collaboration is permitted but MUST respect role boundaries
- Unauthorized actions MUST be rejected and reported
- All agent outputs MUST identify the originating agent

**Rationale**: Role separation ensures accountability, prevents conflicts, and maintains system predictability.

### III. Incremental Evolution

Each phase MUST fully pass before advancing to the next.

- Phase completion requires: specs approved, tests passing, QA agent confirmation
- No phase-skipping is permitted under any circumstances
- Rollback to previous phase is allowed if current phase fails validation
- Phase transitions MUST be documented with completion evidence

**Rationale**: Incremental progression reduces risk, ensures stability, and provides clear milestones for validation.

### IV. Test-Backed Progress

All features MUST be validated by tests.

- No feature is considered complete without passing tests
- Tests MUST be written before or alongside implementation (TDD preferred)
- Test coverage MUST include: happy path, edge cases, error conditions
- Silent test failures are forbidden — all failures MUST be visible and actionable

**Rationale**: Tests provide objective proof of correctness and prevent regressions.

### V. Traceability

Every output MUST be traceable back to a spec requirement.

- Code MUST reference spec requirement IDs in comments or commit messages
- Test cases MUST map to specific acceptance scenarios
- Documentation MUST link to source specifications
- Orphan outputs (not traceable to a spec) MUST be flagged for review

**Rationale**: Traceability ensures completeness, simplifies auditing, and connects implementation to intent.

## Authorized Sub-Agents

The following agents are authorized to operate within this project:

| Agent | Responsibility | Primary Skills |
|-------|---------------|----------------|
| **spec-agent** | Creates and refines specs & constitution | Specification writing, requirements analysis |
| **backend-agent** | Implements FastAPI backend | Python, FastAPI, API design |
| **frontend-agent** | Builds Next.js frontend | TypeScript, React, Next.js |
| **database-agent** | Manages schema and persistence | PostgreSQL, SQLModel, migrations |
| **chatbot-agent** | Implements AI conversational features | NLP, intent mapping, OpenAI integration |
| **event-agent** | Manages Kafka & Dapr event flows | Event-driven architecture, pub/sub |
| **devops-agent** | Handles Docker, Kubernetes, Helm | Containerization, orchestration |
| **qa-agent** | Validates correctness via testing | Test frameworks, validation |

**Collaboration Rules**:
- Agents MAY request information from other agents
- Agents MUST NOT execute tasks outside their defined responsibility
- Disputes between agents are resolved by the constitution (this document)

## Phase Governance

### Phase I: Python CLI Todo (In-Memory)

**Scope**: CRUD operations only, no persistence

- Create, Read, Update, Delete tasks via CLI
- In-memory storage (data lost on exit)
- No external dependencies

**Exit Criteria**: All CRUD operations work, tests pass, QA confirms

### Phase II: Full-Stack Web Application

**Scope**: Web interface with persistence and authentication

- FastAPI backend with REST API
- Next.js frontend with responsive UI
- PostgreSQL database for persistence
- User authentication required

**Exit Criteria**: Full CRUD via web UI, auth working, database persisted, tests pass, QA confirms

### Phase III: AI Chatbot Interface

**Scope**: Natural language task management

- AI-powered chatbot for task operations
- Natural language understanding for CRUD intents
- Deterministic task actions only (no hallucinated data)

**Exit Criteria**: Chat interface functional, NL commands map to actions correctly, tests pass, QA confirms

### Phase IV: Local Kubernetes Deployment

**Scope**: Container orchestration on local infrastructure

- Docker containerization for all services
- Helm charts for deployment configuration
- Minikube for local Kubernetes cluster

**Exit Criteria**: All services deployed to Minikube, inter-service communication working, tests pass, QA confirms

### Phase V: Cloud-Native Deployment

**Scope**: Production-ready cloud infrastructure

- Kafka for event streaming
- Dapr for distributed application runtime
- Managed Kubernetes cluster

**Exit Criteria**: Cloud deployment operational, event flows working, observability in place, tests pass, QA confirms

## Error Handling Requirements

All errors MUST include:
- Root cause identification
- Spec reference (which requirement was violated)
- Suggested fix or remediation path

**Rules**:
- Silent failure is forbidden
- Retry loops MUST be bounded and safe (max retries, exponential backoff)
- Error states MUST be recoverable or explicitly terminal

## Output Requirements

All outputs MUST be:
- **Structured**: Follow defined formats (Markdown for specs, JSON for data)
- **Minimal**: No unnecessary verbosity or redundancy
- **Reusable**: Designed for consumption by other agents or processes
- **Spec-referenced**: Linked to originating requirements

**Preferred Formats**:
- Specifications: Markdown
- Code: Clean, readable, documented
- Test Reports: Clear pass/fail with coverage metrics
- Logs: Structured JSON with correlation IDs

## Final Authority

When conflicts arise, the following hierarchy applies:

1. **The spec overrides assumptions** — If unclear, consult the spec
2. **The constitution overrides agents** — Agent decisions yield to these rules
3. **Safety overrides speed** — Never compromise safety for velocity

## Governance

### Amendment Procedure

1. Propose amendment via spec-agent with rationale
2. Document in `/history/adr/` if architecturally significant
3. Require review and approval before adoption
4. Update version number per semantic versioning rules
5. Propagate changes to dependent templates

### Versioning Policy

- **MAJOR**: Backward-incompatible principle changes or removals
- **MINOR**: New principles, sections, or material expansions
- **PATCH**: Clarifications, typo fixes, non-semantic refinements

### Compliance Review

- All PRs MUST verify compliance with this constitution
- QA agent MUST confirm phase completion criteria before advancement
- Violations MUST be documented and resolved before merge

**Version**: 1.0.0 | **Ratified**: 2026-01-04 | **Last Amended**: 2026-01-04
