"""Exercise clean/incremental migrations and pg_dump/restore on generated synthetic DBs only."""

import json
import re
import subprocess
import time
from pathlib import Path
from uuid import uuid4

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = [
    "docker",
    "compose",
    "--env-file",
    str(ROOT / "deploy/.env.release"),
    "-f",
    str(ROOT / "deploy/compose.release.yaml"),
]


def run(args: list[str], data: str | None = None) -> str:
    result = subprocess.run(
        [*COMPOSE, *args], input=data, text=True, capture_output=True, check=False
    )
    if result.returncode:
        # Never echo subprocess arguments/environment or database exception details.
        raise RuntimeError(
            "Recovery drill command failed; inspect the isolated stack securely"
        )
    return result.stdout.strip()


def sql(statement: str) -> str:
    return run(
        [
            "exec",
            "-T",
            "db",
            "psql",
            "-U",
            "devtreck_owner",
            "-d",
            "postgres",
            "-At",
            "-v",
            "ON_ERROR_STOP=1",
        ],
        statement,
    )


SEED = """
from datetime import UTC, datetime, timedelta
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os
from app.services.accounts import AccountsService
from app.services.tasks import TasksService
from app.services.productivity import ProductivityService
from app.persistence.accounts import AccountsRepository
with Session(create_engine(os.environ['DATABASE_URL'])) as db:
    account = AccountsService(db).register('Synthetic recovery', 'restore@example.com', 'Synthetic drill passphrase')
    AccountsService(db).login(account.email, 'Synthetic drill passphrase')
    tasks = TasksService(db, account.id, 'UTC')
    category = tasks.create_category('Recovery')
    one = tasks.create({'title':'Recover this', 'category_id':category.id})
    tasks.complete(one.id)
    tasks.update(one.id, {'task_type':'daily'})
    habit = tasks.create({'title':'Restored habit','task_type':'daily'})
    tasks.complete(habit.id)
    now = datetime.now(UTC)
    productivity = ProductivityService(db, account.id, 'UTC', lambda: now)
    productivity.add_item(habit.id, 'Restored child')
    productivity.save_plan([], [])
    productivity.command(uuid4(), 'start', seconds=1500)
    now += timedelta(seconds=1500)
    productivity.current()
    AccountsRepository(db).throttle('synthetic-drill-key', 1)
print('Synthetic account/task/habit/session/reward records seeded')
"""

FINGERPRINT = """
import hashlib, json, os
from sqlalchemy import create_engine, text
from app.database.base import Base
import app.persistence.models
result = {}
with create_engine(os.environ['DATABASE_URL']).connect() as db:
    for name in sorted([*Base.metadata.tables, 'alembic_version']):
        rows = sorted(db.execute(text('SELECT to_jsonb(t)::text FROM "'+name+'" t')).scalars())
        result[name] = {'rows':len(rows), 'sha256':hashlib.sha256(json.dumps(rows).encode()).hexdigest()}
print(json.dumps(result, sort_keys=True))
"""


def main() -> None:
    secret = dotenv_values(ROOT / "deploy/.env.release")["RELEASE_DB_PASSWORD"]
    suffix = uuid4().hex
    source, target = "devtreck_drill_" + suffix, "devtreck_restore_" + suffix
    dump = "/tmp/devtreck-drill-" + suffix + ".dump"
    created: list[str] = []

    def api(database: str, command: list[str], data: str | None = None) -> str:
        return run(
            [
                "exec",
                "-T",
                "-e",
                f"DATABASE_URL=postgresql+psycopg://devtreck_owner:{secret}@db:5432/{database}",
                "api",
                *command,
            ],
            data,
        )

    try:
        for database in [source, target]:
            if not re.fullmatch(r"devtreck_(drill|restore)_[0-9a-f]{32}", database):
                raise RuntimeError("Refusing unsafe database name")
            sql(f'CREATE DATABASE "{database}";')
            created.append(database)
        # Clean baseline, then every phase-9 incremental operation.
        api(source, ["alembic", "upgrade", "e5fe82dd46cc"])
        api(source, ["alembic", "upgrade", "head"])
        api(source, ["alembic", "check"])
        api(source, ["python", "-"], SEED)
        expected = json.loads(api(source, ["python", "-"], FINGERPRINT))
        run(
            [
                "exec",
                "-T",
                "db",
                "pg_dump",
                "-U",
                "devtreck_owner",
                "-d",
                source,
                "-Fc",
                "--no-owner",
                "--no-acl",
                "-f",
                dump,
            ]
        )
        started = time.monotonic()
        run(
            [
                "exec",
                "-T",
                "db",
                "pg_restore",
                "-U",
                "devtreck_owner",
                "-d",
                target,
                "--no-owner",
                "--no-acl",
                "--exit-on-error",
                dump,
            ]
        )
        actual = json.loads(api(target, ["python", "-"], FINGERPRINT))
        assert actual == expected, "Restored records differ from source"
        api(target, ["alembic", "check"])
        duration = round(time.monotonic() - started, 2)
        report = {
            "status": "PASS",
            "restore_and_verify_seconds": duration,
            "synthetic_rpo_records_lost": 0,
            "tables": {key: value["rows"] for key, value in actual.items()},
            "all_row_checksums_equal": True,
        }
        output = ROOT / ".release-results"
        output.mkdir(exist_ok=True)
        (output / "recovery.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        print(json.dumps(report, indent=2))
    finally:
        run(["exec", "-T", "db", "rm", "-f", dump])
        for database in reversed(created):
            sql(f'DROP DATABASE "{database}" WITH (FORCE);')


if __name__ == "__main__":
    main()
