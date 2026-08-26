#!/usr/bin/env python3

import argparse
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

DIST_DIR = ROOT / "website" / "dist"
BUILD_SCRIPT = ROOT / "scripts" / "build_website.py"


def run(command, *, capture=False):
    print("+", " ".join(str(part) for part in command))

    result = subprocess.run(
        [str(part) for part in command],
        text=True,
        capture_output=capture,
        check=True,
    )

    if capture:
        return result.stdout.strip()

    return ""


def terraform_output(name):
    value = run(
        [
            "terraform",
            f"-chdir={TF_DIR}",
            "output",
            "-raw",
            name,
        ],
        capture=True,
    )

    if not value:
        raise RuntimeError(
            f"Terraform output {name!r} was empty."
        )

    return value


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Build and deploy AJTayfel.com to the Terraform-managed "
            "S3 bucket and invalidate CloudFront."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually upload files and invalidate CloudFront.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build and show the S3 changes without uploading.",
    )

    args = parser.parse_args()

    if args.apply and args.dry_run:
        parser.error("Choose either --apply or --dry-run, not both.")

    if not args.apply and not args.dry_run:
        print(
            "No deployment mode selected.\n"
            "\n"
            "Use:\n"
            "  python3 scripts/deploy_website.py --dry-run\n"
            "\n"
            "to preview deployment, or:\n"
            "  python3 scripts/deploy_website.py --apply\n"
            "\n"
            "to deploy to the live S3/CloudFront stack."
        )
        return 0

    print("Building production website...")
    run([sys.executable, BUILD_SCRIPT])

    if not DIST_DIR.is_dir():
        raise RuntimeError(
            f"Build directory does not exist: {DIST_DIR}"
        )

    print("Reading deployment targets from Terraform...")

    bucket = terraform_output("website_bucket_name")
    distribution_id = terraform_output(
        "cloudfront_distribution_id"
    )

    print(f"S3 bucket: {bucket}")
    print(f"CloudFront distribution: {distribution_id}")

    sync_command = [
        "aws",
        "s3",
        "sync",
        f"{DIST_DIR}/",
        f"s3://{bucket}/",
        "--delete",
    ]

    if args.dry_run:
        print("\nDRY RUN — no files will be uploaded or deleted.")
        sync_command.append("--dryrun")
        run(sync_command)

        print(
            "\nDry run complete. "
            "CloudFront was not invalidated."
        )
        return 0

    print("\nUploading website...")
    run(sync_command)

    print("\nCreating CloudFront invalidation...")

    run(
        [
            "aws",
            "cloudfront",
            "create-invalidation",
            "--distribution-id",
            distribution_id,
            "--paths",
            "/*",
        ]
    )

    print("\nDeployment complete.")
    print("Verify:")
    print("  https://ajtayfel.com/")
    print(
        "  https://ajtayfel.com/"
        "relocation/chicago-to-southwest-florida/"
    )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(
            f"\nERROR: command failed with exit code "
            f"{exc.returncode}.",
            file=sys.stderr,
        )
        raise SystemExit(exc.returncode)
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
