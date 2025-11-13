## Overview:
This is a AI finance project.
The project is a full stack website develeoped with Python and FastAPI for backend and React.JS for frontend.
A lot of the project is developed in Danish although there is sometimes English as well.

# Repository Guidelines

## Project Structure & Module Organization
- `backend/` FastAPI app: `app/main.py` wires routers, `app/adapters/` holds AI and broker integrations, and `app/routers/` defines HTTP endpoints; keep secrets in `.secrets/` (gitignored).
- `frontend/` React + Vite client with components in `src/components/`, pages in `src/pages/`, shared layout in `src/layouts/`, and prompt helpers in `src/prompts/`.
- `shared/prompts/` contains reusable prompt templates; update both backend `app/adapters/ai` and frontend `src/prompts/` when adding variants.
- Configuration samples live in `backend/.env.example` and `frontend/.env.local`; use them to build local `.env` files but never commit credentials.

## Build, Test, and Development Commands
- `python -m venv .venv && .venv\Scripts\activate` prepares the backend environment; follow with `pip install -r backend/requirements.txt`.
- `uvicorn app.main:app --reload --port 8000` (run inside `backend/app`) starts the API with hot reload.
- `npm install` then `npm run dev` in `frontend/` launches the Vite dev server on port 5173.
- `npm run build` creates optimized frontend assets; `npm run lint` enforces the TypeScript/React lint rules.

## Coding Style & Naming Conventions
- Python: 4-space indentation, full type hints, and Protocol-driven adapters to honor DRY/SOLID; each public function includes a concise intent comment.
- TypeScript: PascalCase components, camelCase hooks/utilities, and descriptive interface names (e.g., `TradeFormProps`); prefer named exports.
- Avoid non-standard abbreviations; industry terms like `params` or `DTO` are acceptable.
- This project tries to use flexible and clean code as much as possible so the user can easily add more functionality later. This is for example achieved by using a interface in   the brokers section.
- The way it will achieve that is by implementing DRY and SOLID principles.
- The naming should focus on being readable. This means only abbrievating for industry standard names like params.
- This program will always try to have comments comments explaining simply what the function does.

## Testing Guidelines
- Backend tests belong in `backend/tests/` (create if missing) and use `pytest`; name files `test_<feature>.py` aligned with routers or adapters.
- Frontend tests should reside in `frontend/src/__tests__/` using Vitest + React Testing Library; add an npm `test` script once suites exist.
- Temporary scripts such as `backend/test.py` are for debugging only; convert them into real tests before merging.

## Commit & Pull Request Guidelines
- Write imperative, descriptive commit subjects (`feat: add Gemini provider registry`) and keep each commit focused.
- Pull requests must summarize the change, include screenshots or sample payloads for UI/API updates, note executed checks (`pytest`, `npm run lint`), and link related issues.
- Request review only after CI passes and secrets are confirmed absent from the diff.

## Security & Configuration Tips
- Store OAuth tokens within `.secrets/` or local `.env` files; never commit them.
- Keep `FRONTEND_ORIGIN` and provider redirect URLs synchronized across env files and dashboards.
- Validate new brokers against the `BrokerAdapter` Protocol before exposing routes or UI entry points.


## Project structure:
AI_TRADER_WEBSITE/
├─ .vscode/
│  └─ settings.json - VS code settings
├─ backend/
│  ├─ .secrets/
│  ├─ .venv/
│  ├─ app/
│  ├─ .env
│  ├─ .env.example
│  ├─ requirements.txt
│  └─ test.py
├─ frontend/
│  ├─ node_modules/        # stort, udeladt indhold
│  ├─ public/
│  ├─ src/
│  ├─ .env.local
│  ├─ .gitignore
│  ├─ eslint.config.js
│  ├─ index.html
│  ├─ package-lock.json
│  ├─ package.json
│  ├─ README.md
│  ├─ tsconfig.app.json
│  ├─ tsconfig.json
│  ├─ tsconfig.node.json
│  └─ vite.config.ts
├─ shared/
│  └─ prompts/
│     ├─ context_prompt.txt
│     ├─ manage_prompt.txt
│     └─ research_prompt.txt
├─ .gitignore
└─ Agents.md