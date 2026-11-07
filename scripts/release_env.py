"""Generate a local-only release environment without printing secrets or overwriting files."""

import secrets
from pathlib import Path


def main() -> None:
    path = Path(__file__).resolve().parents[1] / "deploy" / ".env.release"
    with path.open("x", encoding="utf-8") as stream:
        stream.write(f"RELEASE_DB_PASSWORD={secrets.token_urlsafe(36)}\n")
        stream.write(f"RELEASE_APP_PASSWORD={secrets.token_urlsafe(36)}\n")
    path.chmod(0o600)
    print("Generated ignored local release credentials; no existing file overwritten.")


if __name__ == "__main__":
    main()
