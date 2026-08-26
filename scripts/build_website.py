#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TF_DIR = (
    ROOT
    / "infrastructure"
    / "terraform"
    / "environments"
    / "staging"
)

WEBSITE_DIR = ROOT / "website"


def run(command, *, cwd=None, env=None, capture=False):
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=capture,
        check=True,
    )

    if capture:
        return result.stdout.strip()

    return ""


def main():
    print("Reading relocation API endpoint from Terraform...")

    try:
        api_url = run(
            [
                "terraform",
                f"-chdir={TF_DIR}",
                "output",
                "-raw",
                "relocation_lead_api_endpoint",
            ],
            capture=True,
        )
    except subprocess.CalledProcessError:
        print(
            "ERROR: Could not read relocation API endpoint "
            "from Terraform state.",
            file=sys.stderr,
        )
        return 1

    if not api_url.startswith("https://"):
        print(
            "ERROR: Terraform returned an invalid API endpoint.",
            file=sys.stderr,
        )
        return 1

    env = os.environ.copy()
    env["PUBLIC_RELOCATION_API_URL"] = api_url

    print("Building Astro website with relocation API configured...")

    run(
        ["npm", "run", "build"],
        cwd=WEBSITE_DIR,
        env=env,
    )

    print("Website build complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
