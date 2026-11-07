"""Run real browser journeys in a generated disposable PostgreSQL database."""

import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen
from uuid import uuid4

from dotenv import dotenv_values
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def wait(url: str) -> None:
    for _ in range(120):
        try:
            with urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except URLError, TimeoutError:
            pass
        time.sleep(0.5)
    raise RuntimeError("Browser test service did not start")


def stop(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True, check=False
        )
    else:
        os.killpg(process.pid, signal.SIGTERM)
    process.wait(timeout=15)


def main() -> int:
    api = Path(__file__).resolve().parents[1]
    web = api.parent / "web"
    raw = os.environ.get("TEST_DATABASE_URL") or dotenv_values(api / ".env.test").get(
        "TEST_DATABASE_URL"
    )
    if not raw or make_url(raw).database != "devtreck_test":
        raise RuntimeError("Configure TEST_DATABASE_URL naming devtreck_test")
    url = make_url(raw)
    admin = create_engine(url, isolation_level="AUTOCOMMIT", hide_parameters=True)
    name = "devtreck_browser_" + uuid4().hex
    node = shutil.which("node")
    if not node:
        raise RuntimeError("Node is required")
    env = {
        **os.environ,
        "APP_ENV": "test",
        "DATABASE_URL": url.set(database=name).render_as_string(hide_password=False),
        "ALLOWED_ORIGINS": json.dumps(["http://127.0.0.1:3100"]),
        "API_ORIGIN": "http://127.0.0.1:8010",
        "NEXT_TELEMETRY_DISABLED": "1",
    }
    processes = []
    results = web / "test-results"
    results.mkdir(exist_ok=True)
    with admin.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{name}"'))
    try:
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"], cwd=api, env=env, check=True
        )
        with (web / ".browser-services.log").open("wb") as log:
            processes.append(
                subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "uvicorn",
                        "app.main:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        "8010",
                        "--no-access-log",
                    ],
                    cwd=api,
                    env=env,
                    stdout=log,
                    stderr=log,
                    start_new_session=True,
                )
            )
            wait("http://127.0.0.1:8010/ready")
            processes.append(
                subprocess.Popen(
                    [
                        node,
                        str(web / "node_modules/next/dist/bin/next"),
                        "dev",
                        "--hostname",
                        "127.0.0.1",
                        "--port",
                        "3100",
                    ],
                    cwd=web,
                    env=env,
                    stdout=log,
                    stderr=log,
                    start_new_session=True,
                )
            )
            wait("http://127.0.0.1:3100/login")
            return subprocess.run(
                [node, str(web / "node_modules/@playwright/test/cli.js"), "test", *sys.argv[1:]],
                cwd=web,
                env=env,
                check=False,
            ).returncode
    finally:
        for process in reversed(processes):
            stop(process)
        with admin.connect() as connection:
            connection.execute(text(f'DROP DATABASE "{name}" WITH (FORCE)'))
        admin.dispose()


if __name__ == "__main__":
    sys.exit(main())
