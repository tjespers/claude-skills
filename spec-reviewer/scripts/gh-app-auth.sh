#!/usr/bin/env bash
set -euo pipefail

# GitHub App Auth Wrapper for PR Shepherd
#
# Modes:
#   --check        Verify credentials and print status
#   <command...>   Run command with GH_TOKEN set to app token
#   (no args)      Print GH_TOKEN=xxx to stdout
#
# Required env vars:
#   GITHUB_APP_CLIENT_ID           - GitHub App Client ID (used as JWT issuer)
#   GITHUB_APP_PRIVATE_KEY_PATH    - Path to .pem private key file
#
# Optional env vars:
#   GITHUB_APP_INSTALLATION_ID     - Installation ID (auto-detected from repo if unset)
#
# Config file (sourced if env vars are not already set):
#   ~/.config/pr-shepherd/.env

# --- Load config file if env vars are not set ---
ENV_FILE="${HOME}/.config/pr-shepherd/.env"
if [[ -z "${GITHUB_APP_CLIENT_ID:-}" && -f "$ENV_FILE" ]]; then
  # shellcheck source=/dev/null
  source "$ENV_FILE"
fi

# --- Passthrough when no credentials configured ---
if [[ -z "${GITHUB_APP_CLIENT_ID:-}" || -z "${GITHUB_APP_PRIVATE_KEY_PATH:-}" ]]; then
  if [[ "${1:-}" == "--check" ]]; then
    echo "SKIP: GitHub App credentials not configured. Using default gh auth." >&2
    exit 0
  fi
  if [[ $# -gt 0 ]]; then
    exec "$@"
  fi
  exit 0
fi

# --- Validate inputs ---
CLIENT_ID="$GITHUB_APP_CLIENT_ID"
KEY_PATH="$GITHUB_APP_PRIVATE_KEY_PATH"

if [[ ! -f "$KEY_PATH" ]]; then
  echo "Error: Private key file not found: $KEY_PATH" >&2
  exit 1
fi

# --- Helper: base64url encode (no padding, URL-safe) ---
b64url() {
  openssl enc -base64 -A | tr '+/' '-_' | tr -d '='
}

# --- Token cache ---
CACHE_FILE="/tmp/.pr-shepherd-token-${CLIENT_ID}"

get_cached_token() {
  if [[ -f "$CACHE_FILE" ]]; then
    local token expiry now
    token=$(sed -n '1p' "$CACHE_FILE")
    expiry=$(sed -n '2p' "$CACHE_FILE")
    now=$(date +%s)
    # Valid if expires in more than 5 minutes
    if [[ -n "$expiry" && "$now" -lt $((expiry - 300)) ]]; then
      echo "$token"
      return 0
    fi
  fi
  return 1
}

# --- Try cache first ---
if CACHED=$(get_cached_token); then
  if [[ "${1:-}" == "--check" ]]; then
    echo "OK: GitHub App authentication is configured and working (cached token)." >&2
    exit 0
  fi
  if [[ $# -gt 0 ]]; then
    GH_TOKEN="$CACHED" exec "$@"
  fi
  echo "GH_TOKEN=$CACHED"
  exit 0
fi

# --- Step 1: Generate JWT ---
NOW=$(date +%s)
IAT=$((NOW - 60))
EXP=$((NOW + 540))

HEADER=$(printf '{"alg":"RS256","typ":"JWT"}' | b64url)
PAYLOAD=$(printf '{"iss":"%s","iat":%d,"exp":%d}' "$CLIENT_ID" "$IAT" "$EXP" | b64url)
SIGNATURE=$(printf '%s.%s' "$HEADER" "$PAYLOAD" \
  | openssl dgst -sha256 -sign "$KEY_PATH" -binary \
  | b64url)
JWT="${HEADER}.${PAYLOAD}.${SIGNATURE}"

# --- Step 2: Resolve installation ID ---
INSTALLATION_ID="${GITHUB_APP_INSTALLATION_ID:-}"

if [[ -z "$INSTALLATION_ID" ]]; then
  OWNER_REPO=$(gh repo view --json owner,name --jq '"\(.owner.login)/\(.name)"' 2>/dev/null) || {
    echo "Error: Could not determine owner/repo. Set GITHUB_APP_INSTALLATION_ID manually." >&2
    exit 1
  }

  INSTALLATION_RESPONSE=$(curl -sf \
    -H "Authorization: Bearer $JWT" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${OWNER_REPO}/installation" 2>/dev/null) || {
    echo "Error: App not installed on ${OWNER_REPO}." >&2
    exit 1
  }

  INSTALLATION_ID=$(echo "$INSTALLATION_RESPONSE" | jq -r '.id')

  if [[ "$INSTALLATION_ID" == "null" || -z "$INSTALLATION_ID" ]]; then
    echo "Error: Could not find installation for ${OWNER_REPO}." >&2
    exit 1
  fi
fi

# --- Step 3: Mint installation access token (scoped to minimum permissions) ---
TOKEN_RESPONSE=$(curl -sf -X POST \
  -H "Authorization: Bearer $JWT" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/app/installations/${INSTALLATION_ID}/access_tokens" \
  -d '{"permissions":{"issues":"write","pull_requests":"write"}}' 2>/dev/null) || {
  echo "Error: Failed to create installation token." >&2
  exit 1
}

TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.token')
EXPIRES_AT=$(echo "$TOKEN_RESPONSE" | jq -r '.expires_at')

if [[ "$TOKEN" == "null" || -z "$TOKEN" ]]; then
  echo "Error: Token response did not contain a token." >&2
  exit 1
fi

# --- Cache the token ---
# Try GNU date, then BSD date, then fall back to 1-hour estimate
EXPIRES_EPOCH=$(date -d "$EXPIRES_AT" +%s 2>/dev/null \
  || date -jf "%Y-%m-%dT%H:%M:%SZ" "$EXPIRES_AT" +%s 2>/dev/null \
  || echo $((NOW + 3600)))
printf '%s\n%s\n' "$TOKEN" "$EXPIRES_EPOCH" > "$CACHE_FILE"
chmod 600 "$CACHE_FILE"
echo "Token cached, expires: $EXPIRES_AT" >&2

# --- Output ---
if [[ "${1:-}" == "--check" ]]; then
  echo "OK: GitHub App authentication is configured and working." >&2
  exit 0
fi

if [[ $# -gt 0 ]]; then
  GH_TOKEN="$TOKEN" exec "$@"
fi

echo "GH_TOKEN=$TOKEN"
