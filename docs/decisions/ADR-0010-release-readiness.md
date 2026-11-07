# ADR0010: Local production proof and conditional zero-budget hosting

Status: accepted and deployed for personal use; local and hosted verification passed with documented free-tier limitations.

Package FastAPI and Next with existing dependency locks and immutable base-image digests. Ship Next standalone only for container builds; keep ordinary local builds/start behavior. Use Caddy for loopback HTTPS, same-origin API ingress, headers/body cap and request-free error logs. API/web run as unprivileged users with read-only roots; use a separate one-shot owner-role migration and a restricted runtime DB role. Guard expensive password work with two per-process slots, sanitize unexpected exceptions before the server traceback boundary, and batch daily snapshots.

Prove behavior with existing real-Postgres API/browser regression suites plus release security/query tests, synthetic custom-format backup/restore and a production HTTPS journey. Keep local production-like resources isolated from valuable development data. Serialize outage drills and browser checks. Extend CI without claiming remote success until it actually runs.

User authorized personal-only use, free subdomains, strict $0 and end-to-end deployment after secure sign-in. Final choice is two Vercel Hobby projects (Next and FastAPI) plus Neon Free PostgreSQL. The originally selected Render backend was replaced after explaining its unverifiable account billing safeguards; the official Vercel FastAPI/Python3.14 runtime is compatible and passed the hosted journey. No Render resources or paid services were created.

Retain same-origin rewrites, exact origin checks, restricted database role, explicit owner migrations and certificate-verified direct TLS using certifi. Deploy from a clean worktree to preserve unrelated password-policy edits. Hobby limits and Neon quotas can suspend availability; both Vercel projects share the team allowance. Serverless concurrency multiplies in-process limits/pools; no distributed limiter or load guarantee is implied.

The fresh empty database received authorized additive initialization and is at head8022c27c58ae. A hosted synthetic browser journey passed and its account was deleted. One free baseline snapshot and6-hour provider history exist; scheduled off-provider backups and proposed recovery objectives are not yet operational. See [verified hosting](../deployment/FREE-HOSTING.md), [runbook](../deployment/RUNBOOK.md) and [actual phase evidence](../phase-reports/PHASE-10-REPORT.md). Reconsider hosting before commercial use; no automatic paid upgrade is authorized.
