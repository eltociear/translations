#!/usr/bin/env python3
"""Add a translation PR row to a docs/<category>.md table and recount README.md.

usage: add_entry.py <repo_root> <category> <owner/repo> <pr_number> <file> [<file> ...]

If the repository already has a row, the new files and PR are appended with <br>.
"""
import pathlib
import re
import sys

ROW = re.compile(r"^\|  \[([^\]]+)\]")


def sort_key(name):
    # Letters first (case-insensitive), digit-prefixed repos at the end.
    return (name[0].isdigit(), name.lower())


def main():
    root, category, repo, pr, *files = sys.argv[1:]
    if not files:
        sys.exit(__doc__)
    root = pathlib.Path(root)
    doc = root / "docs" / f"{category}.md"
    lines = doc.read_text().splitlines(keepends=True)
    pr_link = f"[#{pr}](https://github.com/{repo}/pull/{pr})"

    existing = [i for i, l in enumerate(lines) if (m := ROW.match(l)) and m.group(1).lower() == repo.lower()]
    if existing:
        i = existing[0]
        cells = lines[i].rstrip("\n").split("|")
        # cells: ['', repo, files, prs, '']
        if pr_link in cells[3]:
            sys.exit(f"{repo} #{pr} is already listed in {doc}")
        cells[2] = f"  {cells[2].strip()}<br>{'<br>'.join(files)}  "
        cells[3] = f"  {cells[3].strip()}<br>{pr_link}  "
        lines[i] = "|".join(cells) + "\n"
        action = "updated"
    else:
        new = f"|  [{repo}](https://github.com/{repo}/)  |  {'<br>'.join(files)}  |  {pr_link}  |\n"
        rows = [i for i, l in enumerate(lines) if ROW.match(l)]
        pos = next((i for i in rows if sort_key(ROW.match(lines[i]).group(1)) > sort_key(repo)), rows[-1] + 1)
        lines.insert(pos, new)
        action = "added"
    doc.write_text("".join(lines))

    # Recount every category from its rows and rewrite the README table.
    readme = root / "README.md"
    text = readme.read_text()
    total = 0
    for d in sorted((root / "docs").glob("*.md")):
        n = sum(1 for l in d.read_text().splitlines() if ROW.match(l))
        total += n
        text = re.sub(
            rf"(\|  [^|]+?  \|  )\d+(  \|  \[View\]\(docs/{re.escape(d.name)}\))",
            rf"\g<1>{n}\g<2>",
            text,
        )
    text = re.sub(r"\*\*Total\*\*  \|  \*\*\d+\*\*", f"**Total**  |  **{total}**", text)
    readme.write_text(text)
    print(f"{action} {repo} #{pr} in {doc.name}; total {total}")


if __name__ == "__main__":
    main()
