#!/usr/bin/env python3

from pathlib import Path
import argparse
import shutil
from datetime import datetime

parser = argparse.ArgumentParser(
    description="Safely replace a project file."
)

parser.add_argument("target", help="File to replace")
parser.add_argument(
    "--source",
    required=True,
    help="Source file containing the new content"
)

args = parser.parse_args()

target = Path(args.target)
source = Path(args.source)

if not source.exists():
    raise SystemExit(f"Source file not found: {source}")

if target.exists():
    backup = target.with_suffix(
        target.suffix + "." +
        datetime.now().strftime("%Y%m%d-%H%M%S") +
        ".bak"
    )
    shutil.copy2(target, backup)
    print(f"Backup created: {backup}")

shutil.copy2(source, target)

print(f"Updated {target}")
