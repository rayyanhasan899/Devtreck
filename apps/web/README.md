# Devtreck web

Next.js App Router, strict TypeScript and Tailwind. Source: src/app. Shared design tokens: src/app/globals.css. Uses local system fonts; no external font download required.

From this directory: npm ci, npm run dev. Production: npm run build then npm start. Verification: npm run lint and npm run typecheck.

Node 24 is required. The scoped minimatch override patches a transitive lint dependency; npm audit reports zero current findings. ESLint 9 is retained for scaffold compatibility and needs a coordinated future upgrade.

Read ../../README.md for complete API/database setup and ../../docs/phase-reports/PHASE-01-REPORT.md for scope/evidence. This is a welcome page, not the finished task application.
