You are a product manager and system analyst. Your task is to prepare a comprehensive PRD (Product Requirements Document) for an educational MVP of a product called **"Loan Decision Copilot"** – a system that supports bank employees in making loan decisions.

## Context

The application operates as a chat-based interface. The user journey follows this flow:
- An AI agent detects a customer's intent to submit a loan application
- Based on this intent, the system displays a dynamically generated form tailored to the loan type and amount
- The backend retrieves existing customer data and financial history from PostgreSQL
- The system calculates a credit score and returns a decision recommendation with clear justification
- Every decision and action taken must create a complete audit trail for banking compliance requirements
- A separate ADR document will cover architectural details and technology choices; focus this PRD on functionality, system behavior, UX, and UI

## Required Sections

Prepare a document containing the following sections in exactly this order:

### 1. Problem Statement
Describe the business problem this product solves. Focus on the specific pain points of bank employees and customers in the current loan decision process. Be concrete about current inefficiencies, time spent, error rates, or compliance gaps.

### 2. Users / Personas
Describe 2–3 primary personas who will use this system. For each persona, provide:
- Role and responsibility
- Key goals when using the system
- Pain points and frustrations
- Technical proficiency level
- Working context (e.g., call center, office, remote)

### 3. Main Flow
Describe step-by-step how user interactions progress through the system in the happy path scenario. Start from intent detection and end with the recommendation being delivered. Include decision points and system responses at each stage.

### 4. User Stories
Prepare 8–10 user stories in the format: **As a [role], I want [action], so that [benefit]**. Each story should address a specific functional piece (e.g., intent detection, form population, recommendation display, audit logging, data retrieval). Make each story independent and testable.

### 5. Acceptance Criteria
For each user story, provide measurable, testable acceptance criteria. Be specific—replace vague statements like "the system should work fast" with concrete metrics like "the system returns a recommendation within 3 seconds." Include both functional and non-functional criteria where relevant.

### 6. Non-Functional Constraints and Risks

**Non-Functional Constraints:**
- Performance (e.g., max concurrent chat sessions, response time limits)
- Availability and uptime requirements
- Security requirements (data encryption, access control)
- Compliance requirements (regulatory, auditing standards)

**Risks:**
- Technical risks (e.g., scoring algorithm errors, database connection failures, data quality issues)
- Business risks (e.g., poor user adoption, decision bias, regulatory violations)
- User risks (e.g., misunderstanding recommendations, distrust in system)

For each risk, note likelihood, impact, and any mitigation strategy if applicable.

### 7. MVP Scope / Out of Scope

**In Scope:**
Clearly list what functionality is included in this MVP (e.g., basic chat interface, loan type detection, simple scoring, audit trail logging).

**Out of Scope:**
Explicitly list what is intentionally excluded from this MVP (e.g., CRM integration, multi-currency support, advanced reporting, mobile app, API for third-party systems, AI training/fine-tuning, custom workflow rules).

### 8. Test Data Assumptions

Describe the test data that should be prepared for demo and testing. Include:
- Number of demo scenarios (minimum 3–5 covering different outcomes)
- For each scenario: customer profile (income level, credit history, employment status), loan type, loan amount, and expected system recommendation (approval, rejection, or needs verification)
- Any edge cases or boundary conditions to test

## Guidelines

- Write concretely and practically. This is a working document for developers and QA—avoid marketing language.
- For audit trail: explicitly state which actions must be logged (e.g., data retrieved from database, score calculated, recommendation generated, employee viewed recommendation, employee approved/rejected recommendation, timestamp, user ID).
- Focus exclusively on functionality, system behavior, UX, and UI. Do not describe technical architecture, database design, APIs, or technology stack—that belongs in the separate ADR document. However, if technical constraints directly impact user experience (e.g., "system must respond in 3 seconds due to chat UX expectations"), include them.
- If you identify assumptions (e.g., "we assume the PostgreSQL database is always available," "we assume the customer data is always up-to-date"), state them explicitly in a separate "Assumptions" subsection at the end of the document.
- Target document length: 3–5 pages with full section descriptions.

## Final Step

After completing the PRD, ask the user **a minimum of 5 clarifying questions** that would help refine the document further and ensure it aligns with their vision for the Loan Decision Copilot. These questions should address:
- Gaps in the specification you identified while writing
- Ambiguities about user behavior or system behavior
- Constraints or priorities that aren't yet clear
- Edge cases or special scenarios worth validating

Format these questions clearly and number them.