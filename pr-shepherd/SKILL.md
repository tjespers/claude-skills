---
name: pr-shepherd
description: "Proactive PR lifecycle management through a living tracker comment pattern. Creates and maintains a single status comment on PRs that tracks review themes, implementation progress, and deferred items — from PR creation through final approval. Use when: (1) user says 'review came in', 'go over the review', 'handle the review', (2) user asks to respond to PR feedback, (3) user wants to communicate progress on a PR to reviewers, (4) user asks to create or update a PR review response, (5) you proactively detect that review comments need a structured response, (6) user says 'shepherd this PR', 'track this PR', or wants a tracker placed on a newly created PR, (7) user wants to place an initial tracker before reviews arrive, (8) you just created a PR — proactively offer to place an initial tracker."
allowed-tools: Read Edit Bash(gh repo view:*) Bash(gh pr view:*) Bash(gh api repos/:*) Bash(gh api -X PATCH repos/:*) Bash(jq:*) Bash(git add:*) Bash(git commit:*) Bash(bash scripts/gh-app-auth.sh:*)
license: Apache-2.0
metadata:
  author: Tim Jespers <git@tjespers.dev>
  version: 1.0.0
---

# PR Shepherd

Manage the full PR lifecycle through a **living tracker comment** — a single top-level PR comment that serves as the central status hub. Placed at PR creation and updated as reviews arrive, it gives reviewers one place with current status instead of scattered reply threads.

## Context Resolution

Resolve PR context before starting:

```bash
# Get owner/repo from current git remote
gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"'

# Get current PR number (if on a PR branch)
gh pr view --json number --jq '.number'
```

Check for an existing tracker comment to resume from:

```bash
gh api repos/{owner}/{repo}/issues/{pr}/comments --jq '[.[] | select(.body | startswith("## Pull Request Tracker"))] | last | {id, html_url}'
```

If a tracker comment exists, reuse its `id` and `html_url`. Otherwise, create a new one per the workflow below.

## Authentication

Check authentication mode for this session:

```bash
bash scripts/gh-app-auth.sh --check
```

When configured, all **write** operations (creating/updating comments, posting replies) use the auth wrapper so tracker comments appear as a bot identity. Read operations (fetching reviews, PR data) use the user's default `gh` auth.

Prefix write commands with the wrapper — it falls back transparently when app credentials aren't configured.

For **multiline bodies** (tracker comments), use `jq` to safely encode the body into JSON and pipe via `--input -`. This avoids control-character escaping issues with `-f body`:

```bash
BODY=$(cat <<'TRACKER'
...tracker markdown...
TRACKER
)
RESPONSE=$(jq -n --arg body "$BODY" '{body: $body}' | \
  bash scripts/gh-app-auth.sh gh api repos/{owner}/{repo}/issues/{pr}/comments --input -)
```

For **short one-liner bodies** (inline replies), `-f body` is fine:

```bash
bash scripts/gh-app-auth.sh gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies -f body="short message"
```

**Be consistent within a PR.** If the bot created the tracker, all updates must also use bot auth (GitHub requires the comment author to edit their own comments).

For first-time setup, see [references/github-app-setup.md](references/github-app-setup.md).

## Living Tracker Comment

One tracker comment per PR. Created on first use (or at PR creation), updated in-place as review revisions arrive. Never create separate comments per theme or per revision.

### Format

Use the following template. Replace `{placeholders}` with actual values:

```markdown
## Pull Request Tracker — Revision {N}

> This living tracker reflects the current progress of review findings. Updated in-place as themes are addressed.
> current status: {X} of {Y} themes done, {Z} deferred.
> Last updated: {YYYY-MM-DD HH:MM} — all themes resolved.

| # | Theme | Status | Commit |
|---|-------|--------|--------|
| 1 | {description} | ✅ Done | `abc1234` |
| 2 | {description} | 🔄 In Progress | — |
| 3 | {description} | ⏳ Pending | — |

### Theme Details

<details>
<summary><b>1. {Theme name}</b> ✅</summary>

{1-2 sentence summary of what was changed and why}

</details>

<details>
<summary><b>2. {Theme name}</b> 🔄</summary>

{Current approach being taken}

</details>

<details>
<summary><b>3. {Theme name}</b> ⏳</summary>

{Brief description of what will be done}

</details>

<details>
<summary>ℹ️ About this tracker</summary>

This is a living tracker comment managed by [PR Shepherd](https://github.com/tjespers/claude-skills/tree/main/pr-shepherd). It's updated in-place as review themes are addressed, giving reviewers a single place to see current progress.

| Icon | Meaning |
|------|---------|
| ⏳ | Pending |
| 🔄 | In Progress |
| ✅ | Done — committed |
| ❌ | Won't Fix — with explanation |
| 🔀 | Deferred — tracked in ticket/issue |

</details>

🐑 _Created using [PR Shepherd](https://github.com/tjespers/claude-skills/tree/main/pr-shepherd)
🤖 _Updated using [Claude Code](https://claude.com/claude-code)
✈️ _Piloted by [@{owner}](https://github.com/{owner})
```

### Status Icons

| Icon | Meaning |
|------|---------|
| ⏳ | Pending |
| 🔄 | In Progress |
| ✅ | Done — committed |
| ❌ | Won't Fix — with explanation |
| 🔀 | Deferred — tracked in ticket/issue |

### Initial Tracker (pre-review)

When placing a tracker before reviews exist, use this minimal format:

```markdown
## Pull Request Tracker

> Awaiting first review. This tracker will be updated with review themes as they arrive.
> Last updated: {YYYY-MM-DD HH:MM}

| # | Theme | Status | Commit |
|---|-------|--------|--------|
| — | _No review themes yet_ | ⏳ | — |

<details>
<summary>ℹ️ About this tracker</summary>

This is a living tracker comment managed by [PR Shepherd](https://github.com/tjespers/claude-skills/tree/main/pr-shepherd). It's updated in-place as review themes are addressed, giving reviewers a single place to see current progress.

| Icon | Meaning |
|------|---------|
| ⏳ | Pending |
| 🔄 | In Progress |
| ✅ | Done — committed |
| ❌ | Won't Fix — with explanation |
| 🔀 | Deferred — tracked in ticket/issue |

</details>

🐑 _Created using [PR Shepherd](https://github.com/tjespers/claude-skills/tree/main/pr-shepherd)
🤖 _Updated using [Claude Code](https://claude.com/claude-code)
🧑‍✈️ _Piloted by [@{owner}](https://github.com/{owner})
```

When the first review arrives, replace the body with the full Revision 1 template.

## Workflow

### 1. Read and Extract Themes

Fetch review comments:

```bash
gh api repos/{owner}/{repo}/pulls/{pr}/reviews
gh api repos/{owner}/{repo}/pulls/{pr}/comments
```

Group comments into **themes** — related feedback that can be addressed together. A theme is NOT 1:1 with a comment; multiple comments often address the same underlying concern. Group by underlying intent: e.g., three comments about missing null checks across different files = one "add null safety" theme, not three separate items.

**If no review comments are found**: create an initial tracker (see Initial Tracker format above) and stop. The tracker establishes a landing spot for reviewers — when reviews arrive later, run the workflow again. Context Resolution will detect the existing tracker, and the Multiple Review Revisions section covers the Initial → Revision 1 transition.

When reviews exist, group comments into themes and present them to the user with a proposed approach per theme. **Wait for user confirmation** before proceeding.

### 2. Create Tracker Comment

Post a top-level comment with all themes set to ⏳ Pending. Use `jq` to encode the multiline body into valid JSON, then pipe to `gh api` via `--input -`.

Compute dynamic values (like timestamps) **before** the heredoc — single-quoted heredocs (`<<'TRACKER'`) don't expand variables or command substitutions:

```bash
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
BODY=$(cat <<TRACKER
## Pull Request Tracker — Revision 1
...full tracker markdown with $TIMESTAMP where needed...
TRACKER
)
RESPONSE=$(jq -n --arg body "$BODY" '{body: $body}' | \
  bash scripts/gh-app-auth.sh gh api repos/{owner}/{repo}/issues/{pr}/comments --input -)
COMMENT_ID=$(echo "$RESPONSE" | jq -r '.id')
TRACKER_URL=$(echo "$RESPONSE" | jq -r '.html_url')
```

All subsequent updates use `COMMENT_ID`. Use `TRACKER_URL` in inline replies to link back to the tracker.

### 3. Implement and Track

For each theme in order:

1. Update tracker → 🔄 In Progress (`jq -n --arg body "$BODY" '{body: $body}' | bash scripts/gh-app-auth.sh gh api -X PATCH repos/{owner}/{repo}/issues/comments/{id} --input -`)
2. Implement changes
3. Commit
4. Update tracker → ✅ Done with commit hash

**Update after EACH theme**, not in batch. Reviewers watching the PR see incremental progress.

### 4. Inline Replies

After completing a theme, post a one-liner reply on each related review comment:

```bash
bash scripts/gh-app-auth.sh gh api repos/{owner}/{repo}/pulls/{pr}/comments/{comment_id}/replies -f body="Addressed — see [review tracker]({tracker_url}) theme #{n}."
```

Keep inline replies minimal — the tracker has the details.

## Multiple Review Revisions

When reviews arrive on an existing tracker:

1. **Initial → Revision 1**: If the tracker has no "Revision" headings (initial pre-review tracker), replace the body with the full Revision 1 template
2. **Subsequent revisions**: Determine revision number by counting existing "Revision" headings, then **append** a new "Revision {N}" section to the SAME tracker comment
3. Reference previous revisions if themes carry over
4. Maintain chronological record

## Dry Run Mode

When the user requests a dry run (e.g., "show me what the tracker would look like", "test mode", "dry run"), render the full tracker as a markdown code block in the conversation output. Do not make any GitHub API write calls. This lets the user preview and refine the tracker content before posting it live.

Read operations (fetching reviews, PR data) still execute normally — only writes are suppressed.

## Deferred Items

When feedback is valid but out of scope for this PR:

1. Create a ticket/issue for the work
2. Mark as 🔀 Deferred in tracker with ticket link
3. Reply inline: "Valid feedback — tracked in {ticket}. See [review tracker]({tracker_url}) theme #{n}."

## User Alignment Points

Always pause for user input:

- After presenting extracted themes (user may regroup, reprioritize, or reject)
- When a theme requires a judgment call
- Before creating tickets for deferred items
- Before posting the first tracker comment

After the first round is established, subsequent tracker updates proceed without confirmation unless a theme involves a judgment call.

## Anti-Patterns

- **Don't post long inline replies** — one-liners only, detail goes in the tracker
- **Don't batch tracker updates** — update after each theme for visible progress
- **Don't create separate comments per theme** — one tracker, updated in-place
- **Don't skip user alignment on themes** — the user decides the approach, not the agent
- **Don't start implementing before the tracker exists** — create the tracker first so reviewers immediately see the response is being worked on
