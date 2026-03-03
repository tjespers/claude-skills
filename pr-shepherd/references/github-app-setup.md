# GitHub App Setup for PR Shepherd

Setting up a GitHub App allows tracker comments to appear as a bot identity (e.g., `PR Shepherd [bot]`) instead of your personal account. This is **optional** — the skill works without it, using your default `gh` auth.

## Before You Start

- **One app per organization is enough.** A single GitHub App installed on your org covers every repository. You do not need a separate app per repo, per team, or per developer.
- **One person sets it up** (typically an org admin), then distributes the credentials to team members.
- **Each team member** only needs the `.env` file and private key on their machine — no GitHub admin access required after initial setup.

## Step 1: Create a GitHub App

1. Go to **Settings > Developer settings > GitHub Apps > New GitHub App** (use your org's settings page if setting up for a team)
2. Fill in:
   - **App name**: `PR Shepherd` (or any name — this becomes the `[bot]` label)
   - **Homepage URL**: Any valid URL
   - **Webhook**: Uncheck "Active" (not needed)
3. Set **Permissions** (Repository permissions only):
   - **Issues**: Read & Write
   - **Pull requests**: Read & Write
4. Set **Where can this GitHub App be installed?**: "Only on this account"
5. Click **Create GitHub App**
6. Note the **Client ID** shown on the app settings page (a string like `Iv23li4muL7vo9FJG`)

## Step 2: Generate a Private Key

1. On the app settings page, scroll to **Private keys**
2. Click **Generate a private key**
3. A `.pem` file downloads — move it to a secure location:

```bash
mkdir -p ~/.config/pr-shepherd
mv ~/Downloads/*.private-key.pem ~/.config/pr-shepherd/private-key.pem
chmod 600 ~/.config/pr-shepherd/private-key.pem
```

**Never commit this file to any repository.**

## Step 3: Install the App

1. On the app settings page, click **Install App** in the left sidebar
2. Select your account
3. Choose **Only select repositories** and pick the repos where you use PR Shepherd
4. Click **Install**

The installation ID is auto-detected by the auth script — no need to note it down.

## Step 4: Configure Credentials

Create `~/.config/pr-shepherd/.env` (the auth script sources this automatically):

```bash
GITHUB_APP_CLIENT_ID="<your-client-id>"
GITHUB_APP_PRIVATE_KEY_PATH="$HOME/.config/pr-shepherd/private-key.pem"
```

```bash
chmod 600 ~/.config/pr-shepherd/.env
```

## Step 5: Verify

In a repository where the app is installed:

```bash
bash scripts/gh-app-auth.sh --check
```

Expected: `OK: GitHub App authentication is configured and working.`

## Distributing to Your Team

After initial setup, onboarding a new team member takes under 2 minutes:

1. Share the **Client ID** and **private key** file through your org's secret management (1Password, Vault, etc.)
2. Team member runs:

```bash
mkdir -p ~/.config/pr-shepherd
# Place the private key file at:
#   ~/.config/pr-shepherd/private-key.pem
chmod 600 ~/.config/pr-shepherd/private-key.pem
```

3. Team member creates `~/.config/pr-shepherd/.env`:

```bash
GITHUB_APP_CLIENT_ID="<the-shared-client-id>"
GITHUB_APP_PRIVATE_KEY_PATH="$HOME/.config/pr-shepherd/private-key.pem"
```

```bash
chmod 600 ~/.config/pr-shepherd/.env
```

4. Verify: `bash scripts/gh-app-auth.sh --check`

That's it. The auth script auto-detects which repository you're in and resolves the correct installation — no per-repo configuration needed.

## Troubleshooting

| Symptom                                       | Cause                          | Fix                                             |
| --------------------------------------------- | ------------------------------ | ----------------------------------------------- |
| `SKIP: GitHub App credentials not configured` | Missing env vars               | Create `~/.config/pr-shepherd/.env` per Step 4  |
| `Error: Private key file not found`           | Wrong path                     | Check `GITHUB_APP_PRIVATE_KEY_PATH`             |
| `Error: App not installed on owner/repo`      | App not installed on this repo | Install via App settings page                    |
| `Error: Failed to create installation token`  | Wrong permissions              | Check App has Issues + Pull requests read+write |

## Environment Variables

| Variable                      | Required | Description                                                                      |
| ----------------------------- | -------- | -------------------------------------------------------------------------------- |
| `GITHUB_APP_CLIENT_ID`        | Yes      | Client ID from the GitHub App settings page                                      |
| `GITHUB_APP_PRIVATE_KEY_PATH` | Yes      | Absolute path to the `.pem` private key file                                     |
| `GITHUB_APP_INSTALLATION_ID`  | No       | Auto-detected from repo. Set manually for GitHub Enterprise or multi-org setups  |
