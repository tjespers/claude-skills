# PR Shepherd Usage Guide

PR Shepherd is a Claude Code skill that manages PR review communication through a **living tracker comment** — a single, auto-updating comment on your pull request that tracks every piece of review feedback from creation to merge.

## Table of Contents

- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Common Workflows](#common-workflows)
- [GitHub App (Optional)](#github-app-optional)
- [FAQ](#faq)

## How It Works

When you ask Claude to shepherd a PR, it:

1. **Places a tracker comment** on the PR — a single top-level comment that becomes the central status hub
2. **Groups review feedback into themes** — related comments are combined into actionable items, not treated as isolated remarks
3. **Updates the tracker in real-time** — as you work through each theme, the tracker reflects progress with status icons (Pending → In Progress → Done)
4. **Posts one-liner inline replies** on original review comments linking back to the tracker, so reviewers know their feedback was addressed without having to search

The result: reviewers check one place to see what's been addressed, what's in progress, and what's still pending. No scattered reply threads, no "did they see my comment?" uncertainty.

## Getting Started

### Prerequisites

- [Claude Code](https://claude.com/claude-code) installed and configured
- The `pr-shepherd` skill installed (add it to your Claude Code skills)
- `gh` CLI authenticated (`gh auth status`)

### Your First Tracker

The simplest way to start — after creating a PR:

```
> shepherd this PR
```

Claude will place an initial tracker comment on the PR. When reviews come in:

```
> review came in
```

Claude reads the review comments, groups them into themes, presents them for your approval, then creates or updates the tracker and starts working through them.

### Dry Run

Not sure what the tracker will look like? Preview it first:

```
> shepherd this PR, dry run
```

Claude renders the full tracker in the conversation without posting anything to GitHub. Review it, request changes, then tell Claude to post it when you're happy.

## Common Workflows

### Workflow 1: Tracker from PR Creation

Best for when you want reviewers to see the tracker from the start.

1. Create your PR as usual (`gh pr create`, GitHub UI, etc.)
2. Tell Claude: `shepherd this PR` or `track this PR`
3. Claude places an initial "Awaiting review" tracker
4. When reviews arrive: `a review came in` or `go over the review`
5. Claude reads the feedback, groups into themes, updates the tracker
6. Work through themes — tracker updates after each one

### Workflow 2: Respond to an Existing Review

Best for when you already have review feedback to address.

1. Tell Claude: `review came in` or `handle the review`
2. Claude reads the review, groups feedback into themes
3. You approve/adjust the theme grouping
4. Claude creates the tracker and starts implementing
5. Each theme progresses: Pending → In Progress → Done

### Workflow 3: Multiple Review Rounds

The tracker grows with the PR — it doesn't get replaced.

1. First review → Revision 1 section with themes
2. Second review → Revision 2 appended to the same comment
3. Themes from earlier revisions remain visible for context

### Workflow 4: Deferring Items

Some feedback is valid but out of scope for this PR.

1. During theme review, tell Claude to defer an item
2. Claude creates a GitHub issue for the work
3. Tracker marks it as 🔀 Deferred with a link to the issue
4. Inline reply notifies the reviewer with the issue link

## GitHub App (Optional)

By default, tracker comments are posted as **your personal GitHub account**. This works fine, but can look odd when you're also the person being reviewed — you're effectively "responding to yourself."

A GitHub App gives tracker comments their own bot identity (e.g., `PR Shepherd [bot]`), keeping your personal account clean.

### Do I Need One?

- **Solo developer or small team**: Probably not. The skill works perfectly without it.
- **Team adoption**: Recommended. One app covers your entire GitHub organization — every team member's Claude Code uses the same bot identity.

### One App Per Organization

A single GitHub App installation covers all repositories in your organization. You do **not** need to create a separate app per repo, per team, or per user.

Setup flow:
1. **One person** (typically an org admin) creates the GitHub App and installs it on the org
2. **Everyone else** just needs the credentials file (`~/.config/pr-shepherd/.env`) pointing to the shared app's Client ID and private key
3. That's it — the auth script auto-detects the installation for whichever repo you're working in

The private key can be distributed to team members through your org's secret management (1Password, Vault, etc.). Each team member places it at `~/.config/pr-shepherd/private-key.pem`.

For the full step-by-step setup, see [github-app-setup.md](github-app-setup.md).

## FAQ

### Can I use this on any repository?

Yes — any repository where you have push access and `gh` is authenticated. The GitHub App is only needed if you want the bot identity.

### What if I already responded to review comments manually?

No problem. Claude reads all review comments and only creates themes for unresolved feedback. You can also tell Claude to skip specific comments or mark themes as already addressed.

### Does the tracker replace inline review replies?

No. The tracker is the central hub, but Claude also posts short one-liner replies on the original review comments (e.g., "Addressed — see review tracker theme #2"). This way reviewers get notifications on their specific comments.

### Can multiple team members use this on the same PR?

The tracker is tied to whoever (or whichever bot) created it. If using the GitHub App, anyone on the team can update the same tracker since all writes go through the same bot identity. Without the app, only the person who created the tracker can update it (GitHub enforces comment author = editor).

### What happens if I close and reopen the PR?

The tracker comment persists. Claude will find it on the next run and continue from where it left off.

### Can I customize the tracker format?

The format is defined in the skill's SKILL.md. Since it's a local skill, you can modify the templates to match your team's preferences — add columns, change icons, adjust the info block text, etc.
