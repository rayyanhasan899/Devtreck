# API foundation contract

GET /health is public process liveness: 200 {"status":"ok","service":"devtreck-api"}. GET /ready uses a request-scoped session and SELECT 1; same body on 200, safe error on 503. It checks connectivity, not migration version or full feature readiness.

Success bodies are explicit Pydantic endpoint contracts, without a redundant envelope. Errors use {"error":{"code":"...","message":"..."},"request_id":"UUID"}; X-Request-ID matches the body. Every request gets a fresh server ID; untrusted incoming IDs are ignored. OpenAPI declares the error model. Validation returns 422 without echoing input, auth 401/403 and rate-limit 429 behavior will be added with accounts. Domain not-found=404, conflict=409, unavailable/database failure=503, unexpected=500. HTTP errors preserve status but use a safe generic message. Field-specific safe validation details are a future account/form requirement; no sensitive submitted values may be echoed.

Structured application request logs record method, status, elapsed milliseconds and request ID; omit query strings, bodies, cookies, authorization, email and SQL errors. Unexpected logs contain class and ID only, no traceback/exception message. Launch Uvicorn with --no-access-log to prevent its default URL/query access logging from exposing sensitive values. Production remains debug=false.

The future central web client must preserve credentials/CSRF strategy, handle non-2xx envelope and correlation ID, provide accessible errors and reject client-trusted final counters. No feature screens or browser API client introduced before actual account contracts. Routes are unversioned health endpoints; choose feature versioning consistently in phase 3.

## Phase 10 hardening

Unexpected exceptions are sanitized at the middleware boundary before Uvicorn can emit a traceback with private exception text; request IDs/cache policy remain on500 responses. All API responses add X-Content-Type-Options:nosniff. Password work is capped at two concurrent Argon2 operations per process; resource overload returns the existing safe503 unavailable envelope and is retryable without partial account creation. Local HTTPS ingress adds headers and a128KB request cap, omits request objects from proxy errors, and avoids API upstream keepalive reuse. API authorization/CSRF/Origin and source uniqueness remain authoritative. Proxy-level rejection/outage responses can be413/502 rather than application JSON envelopes; centralized browser client handles non-JSON failures safely.
