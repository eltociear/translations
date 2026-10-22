---
name: add-translation
description: Add a Japanese translation PR to the eltociear/translations list, delete the now-unneeded fork, commit and push. Use when the user pastes a GitHub PR URL (https://github.com/<owner>/<repo>/pull/<n>) of their translation work, or asks to add one to translations / the README list, or says "/add-translation <url>".
---

# Add a translation PR to eltociear/translations

Run everything from the root of this repository (remote `origin`, branch `main`).
Layout: `README.md` holds a category table with per-category counts and a Total;
each category is a table in `docs/<category>.md`:

```
|  [owner/repo](https://github.com/owner/repo/)  |  README.ja.md  |  [#123](https://github.com/owner/repo/pull/123)  |
```

Multiple files / PRs in one row are joined with `<br>`.

## Steps (run for each URL the user gives; do not ask for confirmation)

1. **Inspect the PR**
   ```
   gh pr view <n> -R <owner>/<repo> --json state,author,files,headRepository,mergedAt
   gh repo view <owner>/<repo> --json description,repositoryTopics,primaryLanguage
   ```
   - Translated files = files with `changeType: ADDED` that are Japanese docs (e.g. `README.ja.md`, `README_JA.md`, `docs/ja/...`). Ignore edits to other READMEs (language links), `.gitignore`, etc.
   - If the user gave only a repo URL, find their PR with `gh pr list -R <owner>/<repo> --author eltociear --state all`.
   - If the author isn't `eltociear`, stop and tell the user.

2. **Pick the category** from description/topics:
   | file | for |
   | ---- | ---- |
   | `ai-ml` | LLMs, agents, MCP, RAG, ML models, TTS, vision |
   | `web` | web frameworks, frontend, browser stuff |
   | `devtools` | CLIs, editors, libraries, dev tooling |
   | `cloud-infra` | cloud, databases, infra, networking, self-hosting servers |
   | `apps` | end-user desktop/mobile/TV apps |
   | `misc` | anything else (fonts, lists, games, etc.) |
   Mention the chosen category in the report; if it's genuinely ambiguous, pick the closest and say so.

3. **Add the row and recount**
   ```
   python3 .claude/skills/add-translation/scripts/add_entry.py . <category> <owner/repo> <n> <file> [<file> ...]
   ```
   It inserts in case-insensitive alphabetical order (digit-prefixed repos last), or appends to the existing row if the repo is already listed, then recounts every category and the Total in `README.md` from the actual rows. Check `git diff` looks right.

4. **Delete the fork** (only if the PR is `MERGED` or `CLOSED`; if still `OPEN`, keep the fork and tell the user):
   ```
   gh repo delete eltociear/<repo> --yes
   gh repo view eltociear/<repo>   # must fail with "Could not resolve to a Repository"
   ```
   Use the fork name from `headRepository.nameWithOwner` (it may differ from the upstream name).
   If it fails with `delete_repo` scope / HTTP 403, ask the user to run `! gh auth refresh -h github.com -s delete_repo`, then retry.

5. **Commit and push** (push automatically — the user asked for this):
   ```
   git add README.md docs
   git commit -m "docs: update README.md" (plus the attribution trailer, if any)
   git push origin main
   ```
   When several URLs are given at once, add them all and make one commit.

6. **Report** briefly in Japanese: category and row added, count changes (e.g. AI / ML 180→181, Total 308→309), fork deleted (verified), commit hash, and push result.
