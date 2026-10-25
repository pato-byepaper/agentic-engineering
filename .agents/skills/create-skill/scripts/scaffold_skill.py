#!/usr/bin/env python3
"""
scaffold_skill.py
Scaffolds a new Antigravity skill directory structure with frontmatter,
context, references, resources, and scripts directories.
"""

import argparse
import os
import sys
from pathlib import Path


def scaffold_skill(name: str, description: str):
    skill_name = name.lower().strip().replace(" ", "-")
    root = Path.cwd()
    skill_dir = root / ".agents" / "skills" / skill_name

    if skill_dir.exists():
        print(f"Error: Skill directory already exists at {skill_dir}", file=sys.stderr)
        sys.exit(1)

    # Create directory tree
    (skill_dir / "resources").mkdir(parents=True, exist_ok=True)
    (skill_dir / "references").mkdir(parents=True, exist_ok=True)
    (skill_dir / "scripts").mkdir(parents=True, exist_ok=True)
    (skill_dir / "context").mkdir(parents=True, exist_ok=True)

    # 1. Author SKILL.md
    skill_md = f"""---
name: {skill_name}
description: >-
  {description}
---

# {skill_name.replace('-', ' ').title()}

## Project Context
> [!IMPORTANT]
> Consult [context/config.md](./context/config.md) for project-specific configurations before executing.

---

## Workflow

1. Step 1: Initialize and inspect prerequisites.
2. Step 2: Execute task.
3. Step 3: Run verification.

---

## Resources & Scripts

- **Guide**: [guide.md](./references/guide.md)
- **Template**: [template.txt](./resources/template.txt)
- **Helper Script**: [run.sh](./scripts/run.sh)
"""
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    # 2. Author boilerplate helper files
    (skill_dir / "context" / "config.md").write_text(f"# Project Configuration for {skill_name}\n\nAdd repo-specific parameters here.\n", encoding="utf-8")
    (skill_dir / "references" / "guide.md").write_text(f"# Reference Manual: {skill_name}\n\nDetailed checklists and edge cases.\n", encoding="utf-8")
    (skill_dir / "resources" / "template.txt").write_text("# Template placeholder\n", encoding="utf-8")
    
    script_sh = skill_dir / "scripts" / "run.sh"
    script_sh.write_text("#!/usr/bin/env bash\nset -euo pipefail\necho 'Running skill helper...'\n", encoding="utf-8")
    os.chmod(script_sh, 0o755)

    print(f"✅ Successfully scaffolded new skill at: {skill_dir}")
    print(f"   - {skill_dir / 'SKILL.md'}")
    print(f"   - {skill_dir / 'context' / 'config.md'}")
    print(f"   - {skill_dir / 'references' / 'guide.md'}")
    print(f"   - {skill_dir / 'resources' / 'template.txt'}")
    print(f"   - {skill_dir / 'scripts' / 'run.sh'}")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new Antigravity skill.")
    parser.add_argument("name", help="Hyphenated skill name (e.g., db-optimizer)")
    parser.add_argument("description", nargs="?", default="Describe what this skill does and when to use it.", help="Skill trigger description")
    args = parser.parse_args()

    scaffold_skill(args.name, args.description)


if __name__ == "__main__":
    main()
