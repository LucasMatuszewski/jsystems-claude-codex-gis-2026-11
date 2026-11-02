> UWAGA: to opcjonalny przyklad-zalazek do cwiczenia PRD na zywo. NIE nadpisuje
> decyzji grupy - PRD tworzony na kursie (docs/PRD.md) jest jedynym wiazacym.

We are creating a proof of concept (PoC) of a product called **"Hardware Service Decision Copilot"**. We need a system that helps our customer support and hardware service teams decide how to handle complaints and returns.

The application operates first as a form and then as a chat-based interface. The user journey follows this flow:
- User starts with a form asking for:
  - If this is complaint or return (select from a predefined list - 2 options)
  - Type of electronics equipment (select from a predefined list of categories)
  - Name / Model of the equipment (text input)
  - Date of purchase (date picker)
  - Reason for the complaint or return (description, textarea - obligatory for complaints)
  - upload of one image of the equipment showing it's condition (required, showing either that it's not damaged for return or the damage type for complains. BE should handle image compression before sending to multimodal LLM)
- After submitting, the image is sent to the backend and then to the multimodal LLM for analysis (provide different prompts for complaint = judge if damaged and how and what could cause it, and return scenarios = judge if not damaged and if it could be returned and sold again, so no signs of usage)
- Optional (to add later as additional features):
  - The backend retrieves existing customer data and purchase history from SQLite
  - Save in DB every user's session with every decision and action taken in that session
- The agent (powered by thinking LLM) takes the image description from the multimodal LLM, and based on that and the other data provided by the form (from 1st step) and the complaint/return terms/procedures (separate files injected to the prompt as rules to follow based on the Company documents - create some examples of these 2 documents to start with) it returns a decision with clear justification (create separate prompt for return scenario and complaint scenario - based on select field from the form)
- User gets a response with the decision and clear justification from the agent as a first message from the system on the chat interface (first chat bubble, with greetings, decision, explanation and next steps explained - nicely formatted)
- User can interact with the agent on the chat interface, submitting additional information or asking questions, talking with the agent (agent should have full conversation history with data from the form and image description and first message containing the decision and clear justification)
- Optional (to add later as additional features):
  - Agent has internal RAG knowledge base with information about electronics, specifications, and return/complaint procedures

A separate ADR document will cover architectural details and technology choices; focus this PRD on functionality, system behavior, UX, and UI.


---

## Example for AG-UI / CopilotKit app version:

> !!! **Remove it** if you don't use the AG-UI / CopilotKit, **or modify** above prompt if you do !!!

The application operates as a chat-based interface. The user journey follows this flow:
- An AI agent detects a customer's intent to submit a loan application
- Based on this intent, the system displays a dynamically generated form tailored to the loan type and amount
- The backend retrieves existing customer data and financial history from PostgreSQL
- The system calculates a credit score and returns a decision recommendation with clear justification
- Every decision and action taken must create a complete audit trail for banking compliance requirements
- A separate ADR document will cover architectural details and technology choices; focus this PRD on functionality, system behavior, UX, and UI
