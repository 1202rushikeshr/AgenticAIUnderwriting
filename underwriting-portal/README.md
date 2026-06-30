# Insurance Application Portal (Angular)

Purpose: **Application submission only** (no underwriting run/result screens).

## What it calls
`POST {apiBaseUrl}/api/applications/`

## Run
```bash
npm install
npm start
```

Then open: http://localhost:4200

## Backend URL
Edit:
- `src/environments/environment.ts`
- `src/environments/environment.prod.ts`

Default is `http://127.0.0.1:8000`.

## CORS (FastAPI)
Allow `http://localhost:4200` if needed.

Generated: 2026-02-27
