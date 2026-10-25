#!/usr/bin/env python3
"""
new_plan.py
Generates a structured plan markdown artifact in plans/ directory
based on the specified plan type (feature, bugfix, refactor, performance).
"""

import argparse
import datetime
import os
import shutil
import sys
from pathlib import Path


def generate_plan(plan_type: str, name: str):
    root = Path.cwd()
    plans_dir = root / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.datetime.now().strftime("%Y%m%d")
    sanitized_name = name.lower().strip().replace(" ", "-")
    plan_filename = f"{date_str}-{plan_type}-{sanitized_name}.md"
    target_path = plans_dir / plan_filename

    templates_dir = Path(__file__).resolve().parent.parent / "resources"
    template_map = {
        "feature": templates_dir / "feature_plan_template.md",
        "bugfix": templates_dir / "bugfix_plan_template.md",
        "refactor": templates_dir / "refactor_plan_template.md",
        "performance": templates_dir / "performance_plan_template.md",
    }

    template_file = template_map.get(plan_type.lower())
    if not template_file or not template_file.exists():
        print(f"Error: Unknown plan type '{plan_type}'. Valid types: feature, bugfix, refactor, performance", file=sys.stderr)
        sys.exit(1)

    content = template_file.read_text(encoding="utf-8")
    content = content.replace("<Feature Name>", name.title())
    content = content.replace("<Issue Name>", name.title())
    content = content.replace("<Refactor Name>", name.title())
    content = content.replace("<Target Area>", name.title())

    target_path.write_text(content, encoding="utf-8")
    print(f"✅ Created plan artifact at: {target_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate a new engineering plan.")
    parser.add_argument("type", choices=["feature", "bugfix", "refactor", "performance"], help="Type of plan")
    parser.add_argument("name", help="Title or name of the initiative (e.g. user-auth, cart-total-bug)")
    args = parser.parse_args()

    generate_plan(args.type, args.name)


if __name__ == "__main__":
    main()
