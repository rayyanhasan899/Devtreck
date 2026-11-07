# $0 hosting decision and verified deployment

Verified 2026-11-07. Final user authorization is personal/non-commercial use only, free subdomains, strict $0, and end-to-end deployment after secure sign-in. No paid resource, trial, upgrade, card entry or purchased domain was activated.

## Deployed choice

| Layer | Actual resource | Plan and constraints |
|---|---|---|
| Next.js frontend | https://devtreck.vercel.app; project devtreck; Node24 | Vercel Hobby, team raan-899. Personal/non-commercial only; hard usage caps, no paid additional usage. |
| FastAPI | https://devtreck-api.vercel.app; project devtreck-api; Python3.14; fra1 | Same Vercel Hobby allowance, not a second allowance. Function maxDuration60seconds; ephemeral instances, cold starts, no persistent process or local state guarantee. |
| PostgreSQL18 | Neon Free project still-recipe-75029973; production branch br-misty-pond-ba8kkw7s; aws-eu-central-1 | Actual organization plan Free. Compute fixed0.25CU; project quotas set to80CU-hours,4GB transfer and500MB logical data. Six-hour restore history and one manual baseline snapshot. |

The initial Render Free backend was replaced with Vercel FastAPI after comparing the free alternatives and explaining the change. Render may bill bandwidth/build overages when a payment method exists; its public API did not expose sufficient billing safeguards to verify this account's zero-spend requirement. Vercel's officially supported FastAPI/Python3.14 runtime passed the actual hosted journey and keeps both apps within the verified Hobby plan. Render sign-in succeeded, but **no Render service/database/disk was created**. render.yaml remains an unused alternative, not the deployed topology.

Sources checked: [Vercel Hobby](https://vercel.com/docs/plans/hobby), [FastAPI on Vercel](https://vercel.com/docs/frameworks/backend/fastapi), [Python runtime](https://vercel.com/docs/functions/runtimes/python), [Vercel limits](https://vercel.com/docs/limits), [Render Free](https://render.com/docs/free), [Neon plans](https://neon.com/docs/introduction/plans).

## Cost and availability safeguards

Keep Vercel Hobby and Neon Free; do not enable a Pro trial, paid compute, add-on or upgrade. Free quotas can suspend service instead of providing unlimited availability. Vercel resources share team quotas. The inspected Neon live plan table lists100CU-hours,1GB/project and5GB transfer; the configured project quotas are deliberately lower. No Free-plan dollar notification feature is claimed. Review provider usage before increasing traffic; no paid workaround is authorized.

Neon documentation describes mandatory five-minute Free idle suspension, but the endpoint API returned suspend_timeout_seconds=0 and rejected an explicit300-second override under Free policy. Automatic idle suspension was therefore not independently demonstrated. The Free plan and explicit project compute quota remain the spending boundary; availability can stop at that quota. No keepalive scheduler was installed.

## Alternatives reviewed

- **Netlify Free** is the recommended frontend alternative if commercial use returns. Official Free announcement permits commercial projects; current plan docs give300credits/month, hard cap and no auto recharge, with sites pausing at limits. A production deploy consumes15credits, bandwidth20credits/GB and requests2credits/10,000; SSR also consumes compute. Those costs share the same300credit allowance, so20deploys is only a theoretical ceiling with no other use. Its maintained OpenNext adapter supports modern Next>=13.5 including SSR and rewrites; actual Devtreck hosted compatibility still needs a provider build/journey. It was evaluated, not provisioned or substituted for the final user-selected Vercel plan. [Commercial Free plan](https://www.netlify.com/blog/introducing-netlify-free-plan/), [current credit policy](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans/), [Next support](https://docs.netlify.com/build/frameworks/framework-setup-guides/nextjs/overview/).
- **Koyeb** is not a safer $0 backend replacement for this user: official pricing FAQ describes required card validation, a29-dollar hold and possible prorated selected-plan charge. Do not enroll under this authorization. [Official FAQ](https://www.koyeb.com/docs/faqs/pricing).
- **Fly.io** offers a limited free trial/credit rather than a verified indefinite zero-budget backend; not selected. [Official trial](https://docs.fly.io/about/free-trial/).
- **Render free PostgreSQL** explicitly expires after30days; excluded as the long-term database. No paid Render database is authorized.

## Verified compatibility and security

Vercel's Next rewrite keeps browser API calls same-origin. API_ORIGIN is server-only and points to the backend alias. The backend has exact frontend ALLOWED_ORIGINS, production settings and an encrypted restricted-role DATABASE_URL. Direct PostgreSQL TLS uses verify-full, channel binding and an explicit certifi CA bundle; default system trust failed and was fixed without disabling certificate validation. SQLAlchemy's pool is5+5 per instance with pre-ping and10-second connection timeout. Serverless concurrency can multiply connections; this is sized for personal use, not a load-tested public service.

The fresh database was verified empty, initialized with47 Alembic-generated statements in one transaction, and verified at head8022c27c58ae. Runtime role devtreck_app cannot create roles/databases/schema objects. Startup does not run migrations. The user's subsequent end-to-end deployment instruction authorized this additive setup; future destructive migrations still require explicit approval.

Actual public readiness returned200. The hosted browser journey passed in23.3seconds: signup/login, Secure/HttpOnly/SameSiteStrict cookies, task/habit/checklist writes, focus pause/reload/stop,15XP, desktop/mobile, axe, anonymous401, Origin/CSRF403 and account deletion. A database read confirmed zero users after synthetic cleanup. See the [phase report](../phase-reports/PHASE-10-REPORT.md) and [runbook](RUNBOOK.md).

A free manual snapshot snap-broad-dew-bazcsfaj captures the verified empty baseline. It is not an ongoing backup of future user data. Daily off-provider backup scheduling remains unconfigured; proposed24-hour RPO/60-minute RTO are not guarantees. No hosted CI, multi-browser/load test or always-on SLA is claimed.
