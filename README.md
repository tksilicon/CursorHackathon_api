# RentShield — Legal Navigator + Incentive Platform

RentShield is a **role-based platform** for the Northampton rental community with three roles:

- **Admin** — oversees users, properties, tasks, and rewards.
- **Landlord** — creates properties and tasks, reviews submissions, and tracks rewards.
- **Tenant** — completes tasks to earn rewards and accesses AI-powered legal guidance.

It combines:

- An **AI legal navigator** for the **Renters' Rights Act 2025** (in force from 1 May 2026).
- A **task-and-reward system** that encourages positive behaviours (cleanliness, energy saving, community participation) with full Admin oversight.

---

## Core Features

### 1. AI Legal Navigator (RentShield)

- **What just happened?** — Describe your situation; get plain-language guidance with relevant legal context and citations.
- **Notice checker** — Paste a landlord notice; we infer form type (e.g. Section 8), grounds, notice period, and flag issues.
- **Emergency eviction** — One-tap step-by-step guidance and optional voice playback; links to West Northamptonshire Council.
- **Voice support** — MiniMax TTS can read advice aloud for stressed or low-literacy users.

### 2. Roles and Permissions

- **Admin**
  - Create and manage landlord accounts.
  - View all users (landlords and tenants), suspend/activate accounts.
  - View all properties, tasks, submissions, and rewards.
  - Override landlord decisions in disputes; audit approvals.
  - View reports and exports (CSV / PDF) for monthly rewards.

- **Landlord**
  - Manage own properties.
  - Create tasks linked to properties and tenants.
  - Review tenant submissions (approve / reject with feedback).
  - View reward summaries for their tenants.

- **Tenant**
  - View assigned tasks and deadlines.
  - Upload image proof and comments as submissions.
  - Track submission status and reward history.
  - Use RentShield legal tools (What Just Happened, Notice checker, Emergency).

### 3. Data Model (MongoDB)

The app uses the **`rentshield`** database with collections such as:

- `users` — `{ name, email, passwordHash, role: \"admin\" | \"landlord\" | \"tenant\", status }`
- `properties` — `{ landlordId, address }`
- `tasks` — `{ landlordId, tenantId, propertyId, title, description, rewardAmount, deadline, status }`
- `submissions` — `{ taskId, tenantId, imageUrl, comment, submittedAt, status, landlordFeedback, approvedById, approvedAt }`
- `rewards` — `{ tenantId, month, totalReward, paidStatus }`
- `cases`, `notices`, `sessions` — logging for legal advice flows.

---

## Tech Stack

- **Frontend:** Next.js (App Router) + React
- **Backend:** Next.js API routes
- **Database:** MongoDB Atlas (CursorEvent cluster) via official `mongodb` driver
- **AI:** MiniMax LLM (chatcompletion_v2) + MiniMax TTS (t2a_v2)

---

## Setup

1. **Clone and install**

   ```bash
   cd CursorHackaton
   npm install
   ```

2. **Environment**

   Copy `.env.example` to `.env` and set:

   - `MINIMAX_API_KEY` — Your MiniMax API key.
   - `MONGODB_URI` — MongoDB Atlas connection string (replace `<db_password>` with your Atlas user password).
   - `NEXT_PUBLIC_APP_URL` — Base URL for the app (e.g. `http://localhost:3000`).

   The app uses the **`rentshield`** database on your Atlas cluster (created automatically when first written to).

3. **Run**

   ```bash
   npm run dev
   ```

   Then open `http://localhost:3000`.

---

## High-Level Navigation (Planned)

- `/` — Landing page and role chooser.
- `/what-happened` — AI legal navigator: “What just happened?” flow.
- `/notice-checker` — Notice checker.
- `/emergency` — Emergency eviction guidance.
- `/admin/*` — Admin dashboard, user management, reports.
- `/landlord/*` — Landlord dashboard, properties, tasks, submissions, rewards.
- `/tenant/*` — Tenant dashboard, tasks, submissions, reward history + links to legal tools.

Exact routes may evolve as the implementation matures.

---

## Deploy (Vercel)

1. Push the repo to GitHub.
2. Import the project in `https://vercel.com` (Next.js preset).
3. Configure environment variables in Vercel:
   - `MINIMAX_API_KEY`
   - `MONGODB_URI`
   - `NEXT_PUBLIC_APP_URL`
4. Ensure MongoDB Atlas allows connections from Vercel IPs (or for hackathon/demo use, temporarily allow `0.0.0.0/0` and then lock it down later).

---

## Community Impact and Partnerships

This project is designed for **Northampton** and can be piloted with:

- **University of Northampton** — Accommodation Services and Students’ Union (students as tenants).
- **Shelter Northampton** — As a digital triage and self-help tool sitting alongside human advice.
- **Citizens Advice Northampton** — For early-stage self-help before 1:1 appointments.
- **West Northamptonshire Council** — For enforcement (illegal eviction, disrepair) and potential access to anonymised trend data.

Feedback and feature ideas: use GitHub Issues or your chosen contact channel.

---

## Disclaimer

RentShield provides **general information only**, not legal advice. For specific cases, users should contact a housing adviser (for example, Shelter or Citizens Advice) or a qualified solicitor.
