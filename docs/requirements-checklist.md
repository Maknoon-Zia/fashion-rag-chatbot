# Requirements checklist (hackathon brief → implementation)

**Verification dates:** automated tests and manual testing completed on 27 October 2026.

Status legend
* **Verified (auto)** - covered by the automated backend tests (`python -m pytest`), which use in-memory MongoDB/Qdrant and fake AI providers.
* **Verified (manual)** - tested by hand in the running application with real MongoDB Atlas, Qdrant Cloud, Gemini and Groq.
* **Not implemented** - optional feature that was deliberately left out.

| # | Requirement | Where | Status |
|---|---|---|---|
| 1 | Stack: React + Tailwind, FastAPI, Pydantic, MongoDB, Qdrant | whole project | Verified (manual) |
| 2 | Register: client + server validation, unique email, password hashed, no hash returned | `routers/auth.py`, `schemas/auth.py`, `AuthPage.jsx` | Verified (auto + manual) |
| 3 | Login / logout / `me`; token revoked on logout | `auth_service.py`, `deps.py` | Verified (auto + manual) |
| 4 | Protected endpoints reject anonymous/invalid/expired tokens | `deps.py` | Verified (auto) |
| 5 | Create conversation (unique id, owner, title, timestamps) | `POST /api/conversations` | Verified (auto + manual) |
| 6 | Send message: save user message, run RAG, save assistant message | `chat_service.py` | Verified (auto + manual) |
| 7 | Loading state while answering; duplicate submit prevented | `useChat.js`, `Composer.jsx` | Verified (manual) |
| 8 | Failure keeps the user message, no fake answer, Retry without duplicate | `chat_service.py`, `MessageBubble.jsx` | Verified (auto + manual) |
| 9 | History persists after refresh/re-login, bounded and paginated | `GET /api/conversations/{id}` | Verified (auto + manual) |
| 10 | Conversations never mix messages; per-user ownership; 404 for foreign/invalid ids | `conversation_service.py` | Verified (auto + manual) |
| 11 | Sidebar groups Today / Yesterday / Previous 7 Days / Older from `last_message_at`, in the browser's timezone | `utils/dateGroups.js` | Verified (frontend test + manual) |
| 12 | Rename and delete with confirmation; deleted chat returns 404 | `ConversationItem.jsx`, API | Verified (auto + manual) |
| 13 | Auto title from first message (safe truncation) | `derive_title` | Verified (auto + manual) |
| 14 | RAG: query embedding, Qdrant search, retrieved context in the prompt | `retrieval_service.py`, `prompts.py` | Verified (auto + manual); `eval_retrieval`: Recall@5 = 11/11, MRR = 1.00 |
| 15 | Says "cannot find" instead of inventing when evidence is weak | threshold + `NO_ANSWER_MESSAGE` + prompt rule | Verified (manual); threshold calibrated to 0.60 (lowest in-scope top score 0.695, highest out-of-scope 0.508) |
| 16 | Qdrant payload has document id, chunk id, source, access scope | `ChunkMetadata` | Verified (auto) |
| 17 | Same embedding model for documents and queries; safe re-index | `embedding_service.py`, `indexer.py` | Verified (auto + manual ingestion of 99 chunks) |
| 18 | MongoDB indexes (unique email, user + last_message_at, conversation + created_at) | `db/mongo.py` | Verified (auto) |
| 19 | Message length limits, pagination limits, input validation | schemas and Query bounds | Verified (auto) |
| 20 | No stack traces or secrets sent to clients; message content not logged | `core/errors.py` | Verified (auto) |
| 21 | Dependency failures handled with useful errors (LLM, Qdrant) | `errors.py`, services | Verified (auto); Atlas and Gemini outages were not simulated |
| 22 | CORS limited to the configured frontend origin | `main.py` | Verified (manual) |
| 23 | `.env.example` with placeholders, no secrets in code | `backend/.env.example`, `frontend/.env.example` | Verified (manual check before push) |
| 24 | Responsive layout, mobile drawer, empty/loading/error states, Enter / Shift+Enter, reusable components | `frontend/src/components` | Verified (manual) |
| 25 | Tests for auth, ownership, persistence | `backend/tests` (45 tests) | Verified (auto) |
| 26 | README with setup, run, ingestion, API, tests, limitations | `README.md` | Done |
| 27 | Demo / screenshots | `docs/screenshots/`, README "Screenshots" | Done |
| 28 | Connection to real Atlas, Qdrant Cloud, Gemini, Groq | `scripts/check_connections.py` | Verified (manual) |

Optional features: source citations (implemented). Conversation search, streaming and export (not implemented).