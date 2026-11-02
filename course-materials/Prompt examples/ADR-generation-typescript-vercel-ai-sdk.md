> GŁÓWNY wariant kursowy: TypeScript + Vercel AI SDK (stack demonstrowany
> przez trenera). Analogiczny prompt dla Javy:
> ADR-generation-java-openai-sdk-angular-material.md

/write-adr create ADR documents based on @docs/PRD.md

Make research how to implement functionalities from PRD using the below libraries:
https://github.com/vercel/ai
https://ai-sdk.dev/docs

Also evaluate these options I am considering, compare them with the above and say which ones fit this PRD best and why:
- https://chat-sdk.dev/ (ready chat app template built on the AI SDK)
- https://openrouter.ai/docs/api_reference/responses/overview (OpenRouter Responses API)
- https://openrouter.ai/docs/guides/community/vercel-ai-sdk (OpenRouter provider for the Vercel AI SDK)

Read each link before deciding. Prefer the current patterns from these docs over what you remember: they may be newer than your training data.

Use Context7 MCP (`/vercel/ai`) to get the CURRENT documentation - do not rely on your training data.

Research streaming (streamText + useChat) and multimodal input (image upload analyzed by a multimodal LLM). Recommend one approach based on research data.
You should use endpoints from OpenRouter that are specified with example ENV keys in @.env.example
Docs from OpenRouter: https://openrouter.ai/docs

Use Next.js (App Router) with TypeScript strict mode. Research and explain in ADR the best way to initialize this project - remember: we start from an EMPTY app and the agent initializes the template itself.

For the chat UI research ready-to-use components that support streaming out of the box (e.g. AI SDK UI / AI Elements, assistant-ui). ADR should also explain how to combine them with our backend routes and the OpenRouter models, and how the decision flow (formularz -> analiza zdjęcia -> decyzja -> chat) maps to endpoints and components.
