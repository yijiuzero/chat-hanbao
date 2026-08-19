# CLI

`hanbao` is the command-line tool for Hanbao. This page is organized from
"get-up-and-running" to "advanced management" — read from top to bottom if
you're new, or jump to the section you need.

> Not sure what "channels", "heartbeat", or "cron" mean? See
> [Introduction](./intro) first.

---

## Getting started

These are the commands you'll use on day one.

### hanbao init

First-time setup. Walks you through configuration interactively.

```bash
hanbao init              # Interactive setup (recommended for first time)
hanbao init --defaults   # Non-interactive, use all defaults (good for scripts)
hanbao init --force      # Overwrite existing config files
```

**What the interactive flow covers (in order):**

1. **Default Workspace Initialization** — automatically create default workspace and configuration files.
2. **LLM provider** — select provider, enter API key, choose model
   (**required**).
3. **Environment variables** — optionally add key-value pairs for tools.
4. **HEARTBEAT.md** — edit the heartbeat checklist in your default editor.

### hanbao app

Start the Hanbao server. Everything else — channels, cron jobs, the Console
UI — depends on this.

```bash
hanbao app                             # Start on 127.0.0.1:8088
hanbao app --reload                    # Auto-reload on code change (dev)
hanbao app --log-level debug           # Verbose logging
```

| Option        | Default     | Description                                                   |
| ------------- | ----------- | ------------------------------------------------------------- |
| `--host`      | `127.0.0.1` | Bind host                                                     |
| `--port`      | `8088`      | Bind port                                                     |
| `--reload`    | off         | Auto-reload on file changes (dev only)                        |
| `--log-level` | `info`      | `critical` / `error` / `warning` / `info` / `debug` / `trace` |
| `--workers`   | —           | **[DEPRECATED]** Ignored. Hanbao always uses 1 worker        |

> **Note:** The `--workers` option is deprecated for stability reasons. Hanbao is designed to run with a single worker process. Multi-worker mode can cause issues with in-memory state management and WebSocket connections. This option will be removed in a future version.

### hanbao tui

Open the bundled terminal chat UI. It runs Hanbao through the current Python
environment, so it is useful for development installs and shell-first
workflows.

```bash
hanbao                         # Open the TUI with the active agent
hanbao tui --agent writer      # Open the TUI with a specific agent
hanbao .                       # Bind this TUI session to the current project
hanbao tui /path/to/repo       # Bind this TUI session to another project
```

Passing a project directory enables Coding Mode for that TUI session and uses
the directory as the active project. This is session-scoped; it does not write
to `agent.json` or change the project selected in the Console.

### Console

Once `hanbao app` is running, open `http://127.0.0.1:8088/` in your browser to
access the **Console** — a web UI for chat, channels, cron, skills, models,
and more. See [Console](./console) for a full walkthrough.

If the frontend was not built, the root URL returns a JSON message like `{"message": "Hanbao Web Console is not available."}` but the API still works.

**To build the frontend:** in the project's `console/` directory run
`npm ci && npm run build`, then copy the output to the package directory:
`mkdir -p src/hanbao/console && cp -R console/dist/. src/hanbao/console/`.
Docker images and pip packages already include the Console.

### hanbao daemon

Inspect status, version, and recent logs without starting a conversation. Same
behavior as sending `/daemon status` etc. in chat (CLI can show local info when
the app is not running).

| Command                        | Description                                                                               |
| ------------------------------ | ----------------------------------------------------------------------------------------- |
| `hanbao daemon status`        | Status (config, working dir, memory manager)                                              |
| `hanbao daemon restart`       | Print instructions (in-chat /daemon restart does in-process reload)                       |
| `hanbao daemon reload-config` | Re-read and validate config (channel/MCP changes need /daemon restart or process restart) |
| `hanbao daemon version`       | Version and paths                                                                         |
| `hanbao daemon logs [-n N]`   | Last N lines of log (default 100; from `hanbao.log` in working dir)                      |

**Multi-Agent Support:** All commands support the `--agent-id` parameter (defaults to `default`).

```bash
hanbao daemon status                     # Default agent status
hanbao daemon status --agent-id abc123   # Specific agent status
hanbao daemon version
hanbao daemon logs -n 50
```

### hanbao doctor

Read-only diagnostics for your install: root `config.json` validation,
workspaces, `agent.json`, channels, MCP, static console bundle, API
reachability, active LLM / per-agent model checks, and more. **`doctor` by
itself does not repair files** — use the separate **`doctor fix`** subcommand
when you intend to change disk (that path creates backups by default).

```bash
hanbao doctor                      # Default checks
hanbao doctor --deep               # Extra: enabled-channel probes + local llama notes
hanbao doctor --port 8088          # Force API target (see note below)
hanbao doctor fix --dry-run        # Preview planned fixes (no writes)
hanbao doctor fix -y --only …      # Apply allowlisted fixes (see --help)
```

| Option          | Applies to | Purpose                                                               |
| --------------- | ---------- | --------------------------------------------------------------------- |
| `--timeout`     | `doctor`   | HTTP timeout for API / connectivity checks (default 5s)               |
| `--llm-timeout` | `doctor`   | Timeout for model “ping” checks (default 15s)                         |
| `--deep`        | `doctor`   | Outbound probes for enabled channels; extra notes for `hanbao-local` |

**Which host/port does `doctor` hit?** Global `hanbao --host` / `--port`
apply to every subcommand, including `doctor`. If you omit them, the CLI
fills missing values from **`last_api` in `config.json`** (updated when
`hanbao app` last ran). Only when `last_api` is absent do you get
`127.0.0.1:8088`. If checks target the wrong port, pass `--port` explicitly or
update `last_api`.

**`doctor fix`** applies conservative repairs under the working directory
only.

#### Recommended workflow (preview before apply)

```bash
hanbao doctor fix --dry-run
# Narrow to the exact ids you want
hanbao doctor fix --dry-run --only ensure-working-dir,ensure-workspace-dirs

# Apply after you confirm the plan
hanbao doctor fix --only ensure-working-dir,ensure-workspace-dirs
```

- `--dry-run` prints planned operations and does not write files.
- Read-only validations in the plan (such as jobs.json validation) can still
  return non-zero exit codes on FAIL (useful for CI gates).

#### Fix ids at a glance

Pass comma-separated ids with `--only`.

- Common safe examples:
  - `ensure-working-dir` - create working directory if missing
  - `ensure-workspace-dirs` - create missing agent workspace directories
- For the full list of fix ids and risk semantics, run:
  - `hanbao doctor fix --help`
- When `hanbao doctor` detects issues, output includes matching fix hints,
  including suggested `doctor fix --dry-run --only ...` commands.

#### Applying risky ids safely

```bash
hanbao doctor fix --dry-run --only seed-missing-agent-json,reset-invalid-agent-json
hanbao doctor fix -y --only seed-missing-agent-json,reset-invalid-agent-json
```

- Risky ids require `-y` only when applying (without `--dry-run`).
- `--non-interactive` allows only safe + read-only + skill-sync ids and still
  rejects risky ids even with `-y`.

#### Backups and restore

By default, `doctor fix` writes backups to:

- `doctor-fix-backups/<timestamp>/files/`

Restore by copying files from the `files/` subtree back into your working
directory using the same relative paths.

> Avoid `--no-backup` unless you are sure you do not need rollback.

---

## Models & environment variables

Before using Hanbao you need at least one LLM provider configured. Environment
variables power many built-in tools (e.g. web search).

### hanbao models

Manage LLM providers and the active model.

| Command                                  | What it does                                         |
| ---------------------------------------- | ---------------------------------------------------- |
| `hanbao models list`                    | Show all providers, API key status, and active model |
| `hanbao models config`                  | Full interactive setup: API keys → active model      |
| `hanbao models config-key [provider]`   | Configure a single provider's API key                |
| `hanbao models set-llm`                 | Switch the active model (API keys unchanged)         |
| `hanbao models download <repo_id>`      | Download a local model (llama.cpp)                   |
| `hanbao models local`                   | List downloaded local models                         |
| `hanbao models remove-local <model_id>` | Delete a downloaded local model                      |

```bash
hanbao models list                    # See what's configured
hanbao models config                  # Full interactive setup
hanbao models config-key modelscope   # Just set ModelScope's API key
hanbao models config-key dashscope    # Just set DashScope's API key
hanbao models config-key custom       # Set custom provider (Base URL + key)
hanbao models set-llm                 # Change active model only
```

#### Local models

Hanbao can also run models locally via llama.cpp, Ollama, or LM Studio — no API key needed.
But you need to download the corresponding application first, such as [Ollama](https://ollama.com/download) or [LM Studio](https://lmstudio.ai/download).

```bash
# Download a model (auto-selects Q4_K_M GGUF)
hanbao models download Qwen/Qwen3-4B-GGUF

# Download from ModelScope
hanbao models download Qwen/Qwen2-0.5B-Instruct-GGUF --source modelscope

# List downloaded models
hanbao models local

# Delete a downloaded model
hanbao models remove-local <model_id>
hanbao models remove-local <model_id> --yes   # skip confirmation
```

| Option     | Short | Default       | Description                                                           |
| ---------- | ----- | ------------- | --------------------------------------------------------------------- |
| `--source` | `-s`  | `huggingface` | Download source (`huggingface` or `modelscope`)                       |
| `--file`   | `-f`  | _(auto)_      | Specific filename. If omitted, auto-selects (prefers Q4_K_M for GGUF) |

#### Ollama models

Hanbao integrates with Ollama to run models locally. Models are dynamically loaded from your Ollama daemon — install Ollama first from [ollama.com](https://ollama.com).

Install the Ollama SDK: `pip install 'hanbao[ollama]'` (or re-run the installer with `--extras ollama`)

```bash
# Download an Ollama model
ollama pull mistral:7b
ollama pull qwen3:8b

# List Ollama models
ollama list

# Remove an Ollama model
ollama rm mistral:7b

# Use in config flow (auto-detects Ollama models)
hanbao models config           # Select Ollama → Choose from model list
hanbao models set-llm          # Switch to a different Ollama model
```

**Key differences from local models:**

- Models come from Ollama daemon (not downloaded by Hanbao)
- Use `ollama` CLI to manage models (not `hanbao models download/remove-local`)
- Model list updates dynamically when you add/remove via Ollama CLI or Hanbao

> **Note:** You are responsible for ensuring the API key is valid. Hanbao does
> not verify key correctness. See [Config — LLM Providers](./config#llm-providers).

### hanbao env

Manage environment variables used by tools and skills at runtime.

| Command                     | What it does                  |
| --------------------------- | ----------------------------- |
| `hanbao env list`          | List all configured variables |
| `hanbao env set KEY VALUE` | Set or update a variable      |
| `hanbao env delete KEY`    | Delete a variable             |

```bash
hanbao env list
hanbao env set TAVILY_API_KEY "tvly-xxxxxxxx"
hanbao env set GITHUB_TOKEN "ghp_xxxxxxxx"  # fine-grained PATs starting with github_pat_ are also supported
hanbao env delete TAVILY_API_KEY
```

> **Note:** Hanbao only stores and loads these values; you are responsible for
> ensuring they are correct. See
> [Config — Environment Variables](./config#environment-variables).

---

## Channels

Connect Hanbao to messaging platforms.

### hanbao channels

Manage channel configuration (iMessage, Discord, DingTalk, Feishu, QQ,
Console, etc.) and send messages to channels. **Note:** Use `config` for interactive setup (no `configure`
subcommand); use `remove` to uninstall custom channels (no `uninstall`).

**Alias:** You can use `hanbao channel` (singular) as a shorthand for `hanbao channels`.

| Command                   | What it does                                                                       |
| ------------------------- | ---------------------------------------------------------------------------------- |
| `hanbao channels list`   | Show all channels and their status (secrets masked)                                |
| `hanbao channels send`   | Send a one-way message to a user/session via a channel (requires all 5 parameters) |
| `hanbao channels config` | Interactively enable/disable channels and fill in credentials                      |

**Multi-Agent Support:** All commands support the `--agent-id` parameter (defaults to `default`).

```bash
hanbao channels list                    # See default agent's channels
hanbao channels list --agent-id abc123  # See specific agent's channels
hanbao channels config                  # Configure default agent
hanbao channels config --agent-id abc123 # Configure specific agent
```

The interactive `config` flow lets you pick a channel, enable/disable it, and enter credentials. It loops until you choose "Save and exit".

| Channel      | Fields to fill in                                                                    |
| ------------ | ------------------------------------------------------------------------------------ |
| **iMessage** | Bot prefix, database path, poll interval                                             |
| **Discord**  | Bot prefix, Bot Token, HTTP proxy, proxy auth                                        |
| **DingTalk** | Bot prefix, Client ID, Client Secret, Message Type, Card Template ID/Key, Robot Code |
| **Feishu**   | Bot prefix, App ID, App Secret                                                       |
| **QQ**       | Bot prefix, App ID, Client Secret                                                    |
| **Console**  | Bot prefix                                                                           |

> For platform-specific credential setup, see [Channels](./channels).

#### Sending messages to channels (Proactive Notifications)

> Corresponding skill: **Channel Message**

Use `hanbao channels send` to proactively push messages to users/sessions via any configured channel. This is a **one-way send** — no response expected.

When agents have the **channel_message** skill enabled, they can automatically use this command to send proactive notifications when needed.

**Typical use cases:**

- Notify user after task completion
- Scheduled reminders, alerts, status updates
- Push async processing results back to original session
- User explicitly requested "notify me when done"

```bash
# Step 1: Query available sessions
hanbao chats list --agent-id my_bot --channel feishu

# Step 2: Send message using queried parameters
hanbao channels send \
  --agent-id my_bot \
  --channel feishu \
  --target-user ou_xxxx \
  --target-session session_id_xxxx \
  --text "Task completed!"
```

**Required parameters (all 5):**

- `--agent-id`: Sending agent ID
- `--channel`: Target channel (console/dingtalk/feishu/discord/imessage/qq)
- `--target-user`: User ID (get from `hanbao chats list`)
- `--target-session`: Session ID (get from `hanbao chats list`)
- `--text`: Message content

**Important:**

- Always query sessions with `hanbao chats list` first — do NOT guess `target-user` or `target-session`
- If multiple sessions exist, prefer the most recently updated one
- This is for proactive notifications only; for agent-to-agent communication, use `hanbao agents chat` (see "Agents" section below)

**Key differences from `hanbao agents chat`:**

- `hanbao channels send`: Agent-to-user/channel, one-way, no response
- `hanbao agents chat`: Agent-to-agent, bidirectional, with response

---

## Agents

Manage agents and enable inter-agent communication.

### hanbao agents

> Corresponding skill: **Multi-Agent Collaboration**

When agents have the **multi_agent_collaboration** skill enabled, they can automatically use `hanbao agents chat` to collaborate with other agents as needed.

**Alias:** You can use `hanbao agent` (singular) as a shorthand for `hanbao agents`.

| Command                 | What it does                                                                 |
| ----------------------- | ---------------------------------------------------------------------------- |
| `hanbao agents list`   | List all configured agents with their IDs, names, descriptions, workspaces   |
| `hanbao agents create` | Create a new agent configuration and workspace locally                       |
| `hanbao agents delete` | Delete a configured agent (stops it if running, removes from agent list)     |
| `hanbao agents chat`   | Communicate with another agent (bidirectional, supports multi-turn dialogue) |

```bash
# List all agents
hanbao agents list
hanbao agent list  # Same with singular alias

# Create a new agent
hanbao agents create --name "Data Analyst"
hanbao agents create --name "Helper" --template coder --skill web_search --skill pdf_reader
hanbao agents create --name "GPT Bot" --provider-id openai --model-id gpt-4

# Delete an agent (default agent cannot be deleted)
hanbao agents delete my_agent
hanbao agents delete my_agent --remove-workspace  # Also remove workspace directory
hanbao agents delete my_agent --yes                # Skip confirmation

# Chat with another agent (real-time mode, one-shot)
hanbao agents chat \
  --agent-id my_bot \
  --to-agent helper_bot \
  --text "Please analyze this data"

# Multi-turn conversation (session reuse)
hanbao agents chat \
  --agent-id my_bot \
  --to-agent helper_bot \
  --session-id collab_session_001 \
  --text "Follow-up question"

# Complex task (background mode)
hanbao agents chat --background \
  --agent-id my_bot \
  --to-agent data_analyst \
  --text "Analyze /data/logs/2026-03-26.log and generate detailed report"
# Returns [TASK_ID: xxx] [SESSION: xxx]

# Check background task status (--to-agent is optional when querying)
hanbao agents chat --background \
  --task-id <task_id>
# Status flow: submitted → pending → running → finished
# When finished, result shows: completed (✅) or failed (❌)

# Stream mode (incremental response, real-time mode only)
hanbao agents chat \
  --agent-id my_bot \
  --to-agent helper_bot \
  --text "Long analysis task" \
  --mode stream
```

**Required parameters (real-time mode):**

- `--from-agent` (alias: `--agent-id`): Your agent ID (sender)
- `--to-agent`: Target agent ID (recipient)
- `--text`: Message content

**Background task parameters (new):**

- `--background`: Background task mode
- `--task-id`: Check background task status (use with `--background`)

**Optional parameters:**

- `--session-id`: Session ID for multi-turn conversations (auto-generated if omitted)
- `--mode`: Response mode — `final` (default, complete response) or `stream` (incremental)
  - **Note**: `--background` and `--mode stream` are mutually exclusive
- `--base-url`: Override API base URL
- `--timeout`: Timeout in seconds (default: 300)
- `--json-output`: Output full JSON instead of text

**Background mode explanation:**

When tasks are complex (e.g., data analysis, batch processing, report generation), use `--background` to avoid blocking the current agent. After submission, it returns a `task_id` that can be used later to query the task status and result.

**Use cases for background mode**:

- Data analysis and statistics
- Batch file processing
- Generating detailed reports
- Calling slow external APIs
- Complex tasks with uncertain execution time

**Task Status Flow**:

- `submitted`: Task accepted, waiting to start
- `pending`: Queued for execution
- `running`: Currently executing
- `finished`: Completed (result shows `completed` for success or `failed` for error)

**Note:** You can use either `--from-agent` or `--agent-id` — they are equivalent. When checking task status, only `--task-id` is required (`--to-agent` is optional).

**Key differences from `hanbao channels send`:**

- `hanbao agents chat`: Agent-to-agent, bidirectional, returns response
- `hanbao channels send`: Agent-to-user/channel, one-way, no response

---

## Cron (scheduled tasks)

Create jobs that run on a timed schedule — "every day at 9am", "every 2 hours
ask Hanbao and send the reply". **Requires `hanbao app` to be running.**

### hanbao cron

| Command                        | What it does                                  |
| ------------------------------ | --------------------------------------------- |
| `hanbao cron list`            | List all jobs                                 |
| `hanbao cron get <job_id>`    | Show a job's spec                             |
| `hanbao cron state <job_id>`  | Show runtime state (next run, last run, etc.) |
| `hanbao cron create ...`      | Create a job                                  |
| `hanbao cron delete <job_id>` | Delete a job                                  |
| `hanbao cron pause <job_id>`  | Pause a job                                   |
| `hanbao cron resume <job_id>` | Resume a paused job                           |
| `hanbao cron run <job_id>`    | Run once immediately                          |

**Multi-Agent Support:** All commands support the `--agent-id` parameter (defaults to `default`).

### Creating jobs

**Option 1 — CLI arguments (simple jobs)**

Two task types:

- **text** — send a fixed message to a channel on schedule.
- **agent** — ask Hanbao a question on schedule and deliver the reply.

```bash
# Text: send "Good morning!" to DingTalk every day at 9:00 (default agent)
hanbao cron create \
  --type text \
  --schedule-type cron \
  --name "Daily 9am" \
  --cron "0 9 * * *" \
  --channel dingtalk \
  --target-user "your_user_id" \
  --target-session "session_id" \
  --text "Good morning!"

# Agent: create task for specific agent
hanbao cron create \
  --agent-id abc123 \
  --type agent \
  --schedule-type cron \
  --name "Check todos" \
  --cron "0 */2 * * *" \
  --channel dingtalk \
  --target-user "your_user_id" \
  --target-session "session_id" \
  --text "What are my todo items?"

# Agent: run in the background without channel delivery
hanbao cron create \
  --agent-id abc123 \
  --type agent \
  --schedule-type cron \
  --name "Refresh search index" \
  --cron "0 * * * *" \
  --channel console \
  --target-user "your_user_id" \
  --target-session "session_id" \
  --text "Refresh the search index." \
  --silent

# Scheduled one-time task (no repeat)
hanbao cron create \
  --type text \
  --schedule-type scheduled \
  --name "One-time morning reminder" \
  --run-at "2026-05-13T09:00:00+08:00" \
  --channel dingtalk \
  --target-user "your_user_id" \
  --target-session "session_id" \
  --text "Standup starts at 09:00." \
  --save-result-to-inbox

# Calendar-style task: start at a specific time, then repeat daily for 14 runs
hanbao cron create \
  --type text \
  --schedule-type scheduled \
  --name "Two-week standup reminder" \
  --run-at "2026-05-13T09:00:00+08:00" \
  --repeat-every-days 1 \
  --repeat-end-type count \
  --repeat-count 14 \
  --channel dingtalk \
  --target-user "your_user_id" \
  --target-session "session_id" \
  --text "Standup starts at 09:00." \
  --save-result-to-inbox
```

Required fields depend on schedule type:

- `--schedule-type cron`: `--type`, `--name`, `--cron`, `--channel`, `--target-user`, `--target-session`, `--text`
- `--schedule-type scheduled`: `--type`, `--name`, `--run-at`, `--channel`, `--target-user`, `--target-session`, `--text`

For repeating `scheduled` tasks, additionally pass:

- `--repeat-every-days`
- one end condition: `--repeat-end-type count --repeat-count N` or `--repeat-end-type until --repeat-until <ISO8601>`
- or `--repeat-end-type never` for no end

**Option 2 — JSON file (complex or batch)**

```bash
hanbao cron create -f job_spec.json
```

JSON structure matches the output of `hanbao cron get <job_id>`.

### Additional options

| Option                                                 | Default       | Description                                                                 |
| ------------------------------------------------------ | ------------- | --------------------------------------------------------------------------- |
| `--timezone`                                           | user timezone | Schedule timezone (defaults to `user_timezone` from config)                 |
| `--enabled` / `--no-enabled`                           | enabled       | Create enabled or disabled                                                  |
| `--mode`                                               | `final`       | `stream` (incremental) or `final` (complete response)                       |
| `--silent` / `--no-silent`                             | disabled      | Run an `agent` task without delivering its response to the channel          |
| `--save-result-to-inbox` / `--no-save-result-to-inbox` | server rules  | Save execution results to Inbox (if omitted, server-side defaults are used) |
| `--repeat-every-days`                                  | no repeat     | `--schedule-type scheduled` only; repeat every N days                       |
| `--repeat-end-type`                                    | `never`       | For repeated scheduled jobs: `never` / `until` / `count`                    |
| `--repeat-until`                                       | —             | Required when `--repeat-end-type until`; ISO 8601 end datetime              |
| `--repeat-count`                                       | —             | Required when `--repeat-end-type count`; max run count                      |
| `--base-url`                                           | auto          | Override the API base URL                                                   |

### Cron expression cheat sheet

Five fields: **minute hour day month weekday** (no seconds).

| Expression     | Meaning                   |
| -------------- | ------------------------- |
| `0 9 * * *`    | Every day at 9:00         |
| `0 */2 * * *`  | Every 2 hours on the hour |
| `30 8 * * 1-5` | Weekdays at 8:30          |
| `0 0 * * 0`    | Sunday at midnight        |
| `*/15 * * * *` | Every 15 minutes          |

---

## Chats (sessions)

Manage chat sessions via the API. **Requires `hanbao app` to be running.**

### hanbao chats

**Alias:** You can use `hanbao chat` (singular) as a shorthand for `hanbao chats`.

| Command                                  | What it does                                                  |
| ---------------------------------------- | ------------------------------------------------------------- |
| `hanbao chats list`                     | List all sessions (supports `--user-id`, `--channel` filters) |
| `hanbao chats get <id>`                 | View a session's details and message history                  |
| `hanbao chats create ...`               | Create a new session                                          |
| `hanbao chats update <id> --name "..."` | Rename a session                                              |
| `hanbao chats delete <id>`              | Delete a session                                              |

**Multi-Agent Support:** All commands support the `--agent-id` parameter (defaults to `default`).

```bash
hanbao chats list                        # Default agent's chats
hanbao chats list --agent-id abc123      # Specific agent's chats
hanbao chats list --user-id alice --channel dingtalk
hanbao chats get 823845fe-dd13-43c2-ab8b-d05870602fd8
hanbao chats create --session-id "discord:alice" --user-id alice --name "My Chat"
hanbao chats create --agent-id abc123 -f chat.json
hanbao chats update <chat_id> --name "Renamed"
hanbao chats delete <chat_id>
```

---

## Skills

Extend Hanbao's capabilities with skills (PDF reading, web search, etc.).

### hanbao skills

| Command                    | What it does                                              |
| -------------------------- | --------------------------------------------------------- |
| `hanbao skills install`   | Install a skill from a supported URL source               |
| `hanbao skills uninstall` | Remove a skill from the skill pool or one agent workspace |
| `hanbao skills list`      | Show all skills and their enabled/disabled status         |
| `hanbao skills config`    | Interactively enable/disable skills (checkbox UI)         |
| `hanbao skills info`      | Show local details for one workspace skill                |

**Multi-Agent Support:** All commands support the `--agent-id` parameter (defaults to `default`).

```bash
hanbao skills install https://skills.sh/owner/repo/skill  # Import into the local skill pool
hanbao skills install https://skills.sh/owner/repo/skill --agent-id abc123  # Import directly into a specific agent workspace
hanbao skills uninstall skill-creator  # Remove from the local skill pool
hanbao skills uninstall skill-creator --agent-id abc123  # Remove from a specific agent workspace
hanbao skills list                   # See default agent's skills
hanbao skills list --agent-id abc123 # See specific agent's skills
hanbao skills config                 # Configure default agent
hanbao skills config --agent-id abc123 # Configure specific agent
hanbao skills info [skill_name]               # See default agent's skill details
hanbao skills info [skill_name] --agent-id abc123 # See specific agent's skill details
```

In the interactive UI: ↑/↓ to navigate, Space to toggle, Enter to confirm.
A preview of changes is shown before applying.

> For built-in skill details and custom skill authoring, see [Skills](./skills).

---

## Maintenance

### hanbao clean

Remove everything under the working directory (default `~/.hanbao`).

```bash
hanbao clean             # Interactive confirmation
hanbao clean --yes       # No confirmation
hanbao clean --dry-run   # Only list what would be removed
```

---

## Global options

Every `hanbao` subcommand inherits:

| Option          | Default     | Description                                      |
| --------------- | ----------- | ------------------------------------------------ |
| `--host`        | `127.0.0.1` | API host (auto-detected from last `hanbao app`) |
| `--port`        | `8088`      | API port (auto-detected from last `hanbao app`) |
| `-h` / `--help` |             | Show help message                                |

If the server runs on a non-default address, pass these globally:

```bash
hanbao --host 0.0.0.0 --port 9090 cron list
```

## Working directory

All config and data live in `~/.hanbao` by default:

- **Global config**: `config.json` (providers, environment variables, agent list)
- **Agent workspaces**: `workspaces/{agent_id}/` (each agent's independent config and data)

```
~/.hanbao/
├── config.json              # Global config
└── workspaces/
    ├── default/             # Default agent workspace
    │   ├── agent.json       # Agent config
    │   ├── chats.json       # Conversation history
    │   ├── jobs.json        # Cron jobs
    │   ├── AGENTS.md        # Persona files
    │   └── memory/          # Memory files
    └── abc123/              # Other agent workspace
        └── ...
```

| Variable              | Description                         |
| --------------------- | ----------------------------------- |
| `HANBAO_WORKING_DIR` | Override the working directory path |
| `HANBAO_CONFIG_FILE` | Override the config file path       |

See [Config & Working Directory](./config) and [Multi-Agent](./multi-agent) for full details.

---

## Command overview

| Command             | Subcommands                                                                          | Requires server? |
| ------------------- | ------------------------------------------------------------------------------------ | :--------------: |
| `hanbao init`      | —                                                                                    |        No        |
| `hanbao app`       | —                                                                                    |  — (starts it)   |
| `hanbao desktop`   | —                                                                                    |  — (starts it)   |
| `hanbao doctor`    | `fix`                                                                                |        No        |
| `hanbao daemon`    | `status` · `restart` · `reload-config` · `version` · `logs`                          |        No        |
| `hanbao models`    | `list` · `config` · `config-key` · `set-llm` · `download` · `local` · `remove-local` |        No        |
| `hanbao env`       | `list` · `set` · `delete`                                                            |        No        |
| `hanbao channels`  | `list` · `send` · `install` · `add` · `remove` · `config`                            |     **Yes**      |
| `hanbao agents`    | `list` · `create` · `delete` · `chat`                                                |    Partial ¹     |
| `hanbao cron`      | `list` · `get` · `state` · `create` · `delete` · `pause` · `resume` · `run`          |     **Yes**      |
| `hanbao chats`     | `list` · `get` · `create` · `update` · `delete`                                      |     **Yes**      |
| `hanbao skills`    | `install` · `uninstall` · `list` · `config` · `info`                                 |        No        |
| `hanbao task`      | —                                                                                    |        No        |
| `hanbao auth`      | `reset-password`                                                                     |        No        |
| `hanbao plugin`    | `install` · `list` · `info` · `uninstall` · `validate`                               |        No        |
| `hanbao acp`       | —                                                                                    |        No        |
| `hanbao clean`     | —                                                                                    |        No        |
| `hanbao shutdown`  | —                                                                                    |        No        |
| `hanbao update`    | —                                                                                    |        No        |
| `hanbao uninstall` | —                                                                                    |        No        |

¹ `create` does not require server; `list`, `delete`, and `chat` require server.

---

## Related pages

- [Introduction](./intro) — What Hanbao can do
- [Console](./console) — Web-based management UI
- [Channels](./channels) — DingTalk, Feishu, iMessage, Discord, QQ setup
- [Heartbeat](./heartbeat) — Scheduled check-in / digest
- [Skills](./skills) — Built-in and custom skills
- [Config & Working Directory](./config) — Working directory and config.json
- [Multi-Agent](./multi-agent) — Multi-agent setup, management, and collaboration
