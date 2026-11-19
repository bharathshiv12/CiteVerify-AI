# CiteVerify AI - Frontend Application

Next.js (App Router) + TypeScript + Tailwind CSS client interface for CiteVerify AI.

---

## 1. Quick Start

### Install Dependencies
```bash
npm install
```

### Configure Environment
```bash
cp .env.example .env.local
```
Configure `NEXT_PUBLIC_API_BASE_URL` (default: `http://localhost:8000`).

### Run Development Server
```bash
npm run dev
```
Open `http://localhost:3000` in your browser.

### Build Production Bundle
```bash
npm run build
npm run start
```

---

## 2. Directory Structure
- `app/`: Next.js App Router pages and layout.
- `components/`: UI components (upload dropzone, claim tables, evidence cards, review modal).
- `services/`: API client (`api.ts`) communicating with the backend.
- `types/`: Canonical TypeScript interfaces derived from `contracts/schemas/`.
- `public/`: Static assets.

---

## 3. Ownership & Mock Data Policy
- **Owner**: Agent 1 (Frontend Developer)
- **Synthetic Mocks**: Set `NEXT_PUBLIC_USE_MOCKS=true` to load fixture data from `contracts/examples/`. A prominent "SAMPLE DATA" banner must always appear when mock mode is enabled.

