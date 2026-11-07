"""Local loopback release-stack checks, including reversible API shutdown/recovery."""

import hashlib
import http.client
import json
import ssl
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = [
    "docker",
    "compose",
    "--env-file",
    str(ROOT / "deploy/.env.release"),
    "-f",
    str(ROOT / "deploy/compose.release.yaml"),
]


def run(args: list[str]) -> str:
    result = subprocess.run(
        [*COMPOSE, *args], text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError("Local release check command failed")
    return result.stdout.strip()


def main() -> None:
    output = ROOT / ".release-results"
    output.mkdir(exist_ok=True)
    certificate = output / "caddy-root.crt"
    run(["cp", "proxy:/data/caddy/pki/authorities/local/root.crt", str(certificate)])
    context = ssl.create_default_context(cafile=str(certificate))

    def request(
        path: str,
        method: str = "GET",
        body: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, dict[str, str]]:
        connection = http.client.HTTPSConnection(
            "localhost", 8443, context=context, timeout=10
        )
        try:
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            result = (
                response.status,
                {key.lower(): value for key, value in response.getheaders()},
            )
            response.read()
            return result
        finally:
            connection.close()

    assert request("/ready")[0] == 200
    status, headers = request("/api/progress")
    assert status == 401 and headers["cache-control"] == "no-store"
    assert headers["x-content-type-options"] == "nosniff"
    assert "max-age=" in headers["strict-transport-security"]
    # Proxy request cap is tested before application parsing/validation.
    assert (
        request(
            "/api/auth/login",
            "POST",
            "x" * 140000,
            {"Origin": "https://localhost:8443", "Content-Type": "application/json"},
        )[0]
        == 413
    )
    email = "spoof-" + uuid4().hex + "@example.com"
    email_key = hashlib.sha256(("login-email:" + email).encode()).hexdigest()
    key_sql = (
        "SELECT key FROM rate_limits WHERE key <> '" + email_key + "' ORDER BY key;"
    )

    def rate_keys() -> str:
        return run(
            [
                "exec",
                "-T",
                "db",
                "psql",
                "-U",
                "devtreck_owner",
                "-d",
                "devtreck_release",
                "-At",
                "-c",
                key_sql,
            ]
        )

    for index, spoof in enumerate(["198.51.100.1", "203.0.113.2"]):
        assert (
            request(
                "/api/auth/login",
                "POST",
                json.dumps({"email": email, "password": "Wrong synthetic password"}),
                {
                    "Origin": "https://localhost:8443",
                    "Content-Type": "application/json",
                    "X-Forwarded-For": spoof,
                },
            )[0]
            == 401
        )
        if index == 0:
            first_keys = rate_keys()
        else:
            assert rate_keys() == first_keys, (
                "Untrusted forwarding header changed rate-limit identity"
            )
    assert (
        run(
            [
                "exec",
                "-T",
                "db",
                "psql",
                "-U",
                "devtreck_owner",
                "-d",
                "devtreck_release",
                "-At",
                "-c",
                "SELECT rolsuper OR rolcreatedb OR rolcreaterole OR has_schema_privilege('devtreck_app','public','CREATE') FROM pg_roles WHERE rolname='devtreck_app';",
            ]
        )
        == "f"
    )
    assert (
        int(
            run(
                [
                    "exec",
                    "-T",
                    "api",
                    "python",
                    "-c",
                    "import os; from pathlib import Path; assert not Path('/app/.env').exists(); print(os.getuid())",
                ]
            )
        )
        > 0
    )
    assert (
        int(
            run(
                [
                    "exec",
                    "-T",
                    "web",
                    "node",
                    "-e",
                    "if(require('fs').existsSync('/app/.env'))process.exit(1); console.log(process.getuid())",
                ]
            )
        )
        > 0
    )
    marker = "private-proxy-check-" + uuid4().hex
    since = datetime.now(UTC).isoformat()
    try:
        run(["stop", "-t", "25", "api"])
        assert (
            request("/ready?private=" + marker, headers={"X-CSRF-Token": marker})[0]
            == 502
        )
        logs = subprocess.run(
            [*COMPOSE, "logs", "--since", since, "proxy"],
            text=True,
            capture_output=True,
            check=True,
        )
        assert marker not in logs.stdout + logs.stderr
        assert '"request":' not in logs.stdout + logs.stderr
    finally:
        run(["start", "api"])
    for _ in range(40):
        if request("/ready")[0] == 200:
            break
        time.sleep(0.5)
    else:
        raise RuntimeError("Local API did not recover")
    report = {
        "status": "PASS",
        "verified_private_ca_tls": True,
        "request_cap_413": True,
        "untrusted_forwarding_headers_ignored": True,
        "restricted_runtime_role": True,
        "nonroot_app_processes": True,
        "api_shutdown_outage_recovery": True,
        "sanitized_proxy_failure_logs": True,
    }
    (output / "checks.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
