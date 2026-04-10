---
name: software-prototyper-gt-cli
version: 0.12.1
description: |
  Gas Town (gt) CLI complete reference — multi-agent orchestration for AI coding assistants.
  gt/bd/bv 命令行完整参考，覆盖工作分派(sling)、convoy管理、beads问题跟踪、agent监控恢复、
  邮件通信、合并队列、服务生命周期、crew工作区等全部工作流。
  Use whenever working with gt, bd, bv, or any Gas Town concept: dispatch, convoy, polecat,
  rig, sling, mayor, deacon, witness, refinery, crew, hook, molecule, formula, merge queue,
  dolt, daemon, mail, nudge, escalate, beads, agent management, or troubleshooting.
  即使只是"怎么分派任务"或"agent卡住了怎么办"这类问题，也应使用此技能。
---

# Gas Town CLI Reference (v0.12.1)

## Mental Model

Gas Town orchestrates AI coding agents across git repositories.

```
Town (~/gt/)                          Three CLIs:
├── Mayor (global coordinator)          gt  — orchestration & agent management
├── Deacon (daemon watchdog)            bd  — beads issue CRUD
├── Dogs (infra workers)                bv  — beads graph analysis (TUI)
├── Rig: project-A/
│   ├── Crew (human workspaces)       Design: Zero Framework Cognition (ZFC)
│   ├── Witness (agent monitor)       Go provides transport (commands, data).
│   ├── Refinery (merge queue)        Agents provide cognition (decisions).
│   └── Polecats (worker agents)
└── Rig: project-B/
    └── [same structure]
```

**Key concepts**: Town > Rig > Agents. Beads are issues stored in Dolt. Convoys bundle beads for parallel dispatch. Hooks pin work to agents (survive crashes). Molecules track workflow steps. Formulas are TOML workflow templates.

## Quick Orientation

```bash
gt status                  # Overall town status (agents, rigs, services)
gt whoami                  # Current identity for mail commands
gt info                    # Gas Town information and what's new
gt rig list                # List all rigs
gt agents list             # List all agent sessions
gt agents menu             # Interactive session switcher popup
gt vitals                  # Unified health dashboard
gt prime                   # Output role context for current directory
gt feed                    # Real-time activity feed
```

## I want to...

| Goal | Command |
|------|---------|
| Dispatch work to an agent | `gt sling <bead> <rig>` |
| Check what agents are doing | `gt agents list` then `gt peek <session>` |
| See system health | `gt vitals` or `gt health` |
| Send message to an agent | `gt nudge <session> "msg"` |
| Check the merge queue | `gt mq list <rig>` then `gt refinery status` |
| Recover a stuck agent | `gt peek` → `gt nudge` → `gt handoff` → `gt polecat nuke` |
| Start/stop everything | `gt up` / `gt down` |
| Create issues | `bd create --title "..." --type=task` |
| Manage crew workspace | `gt crew add/start/at/refresh` |
| Check costs | `gt costs` |
| Store a memory | `gt remember "insight" --type feedback` |
| File a warrant for stuck agent | `gt warrant file <agent>` |
| Cycle between sessions | `gt cycle next` / `gt cycle prev` |

## Core Workflows

### 1. Dispatch Work (Sling)

The unified work dispatch command. Handles polecats, crew, mayor, dogs.

```bash
# Basic dispatch
gt sling <bead> <rig>                     # Auto-spawn polecat in rig
gt sling <bead> <rig>/<polecat>           # Specific polecat
gt sling <bead> <rig> --crew <name>       # Target crew member
gt sling <bead> mayor                     # Dispatch to Mayor
gt sling <bead> deacon/dogs               # Auto-dispatch to idle dog

# Options
gt sling <bead> <rig> --force             # Ignore unread mail
gt sling <bead> <rig> --formula <name>    # Use specific formula
gt sling <bead> <rig> --var key=val       # Pass formula variables
gt sling <bead> <rig> -a "instructions"   # Natural language args
gt sling <bead> <rig> --no-convoy         # Skip auto-convoy
gt sling <bead> <rig> --merge=direct      # Merge strategy (direct|mr|local)
gt sling <bead> <rig> --ralph             # Ralph Wiggum loop mode

# Batch dispatch
gt sling <id1> <id2> <id3> <rig>          # Multiple beads → multiple polecats

# Formula slinging
gt sling mol-release mayor/               # Cook formula + wisp + attach + nudge
gt sling shiny --on <bead> <rig>          # Apply formula to existing bead

# Undo
gt unsling <bead>                         # Remove work from agent's hook
gt release <bead>                         # Release stuck in_progress → pending
```

**Flow**: `gt sling` → spawn polecat → auto-convoy → cook formula → hook bead → start session

### 2. Convoy Management

Convoys bundle beads for parallel execution with dependency-aware wave feeding.

```bash
gt convoy create <name> [issues...]       # Create convoy
gt convoy stage <epic-id>                 # Analyze deps, compute waves
gt convoy launch <convoy-id>              # Launch staged convoy (dispatch Wave 1)
gt convoy status <convoy-id>              # Show convoy status
gt convoy list                            # List convoys (dashboard view)
gt convoy check <convoy-id>               # Check and auto-close completed
gt convoy stranded                        # Find stranded convoys
gt convoy add <convoy-id> <bead>          # Add issues to existing convoy
gt convoy close <convoy-id>               # Close convoy
gt convoy land <convoy-id>                # Land owned convoy (cleanup + close)
```

**Event-driven feeding**: When an issue closes, the daemon finds its convoy and auto-dispatches the next ready issue.

### 3. Beads Issue Tracking (bd / bv)

Beads are git-backed issues stored in Dolt databases. Two external CLIs.

```bash
# CRUD
bd create --title "..." --type=task --priority=2
bd show <id>                              # Full details with dependencies
bd list --status=open                     # List open issues
bd ready                                  # Unblocked issues ready to work
bd close <id>                             # Mark complete

# Dependencies
bd dep add <from> <to> --type=blocks      # Add blocking dependency

# Formulas
bd formula list                           # List available formulas
bd cook <formula>                         # Formula → Proto (instantiate)

# Graph analysis
bv --robot-triage                         # Graph-aware ranked picks (NEVER bare `bv`)

# Sync
bd sync                                   # Sync with git
```

**Bead IDs**: prefix + 5-char alphanumeric (e.g., `gt-abc12`). Prefix determines database routing.

For details, read `references/beads-cli.md`.

### 4. Agent Monitoring & Recovery

```bash
# Observe
gt agents list                            # List all sessions
gt agents menu                            # Interactive session popup
gt peek <session>                         # View recent output
gt trail                                  # Recent agent activity
gt trail commits / beads / hooks          # Filtered views

# Health
gt vitals                                 # Unified health dashboard
gt health                                 # Comprehensive system health
gt doctor                                 # Run health checks on workspace

# Recovery
gt nudge <session> "message"              # Synchronous message to worker
gt broadcast "message"                    # Nudge all workers
gt handoff                                # Hand off to fresh session
gt seance                                 # Talk to predecessor sessions
gt cleanup                                # Clean orphaned Codex processes

# Polecat lifecycle
gt polecat list <rig>                     # List polecats
gt polecat status <rig>/<name>            # Detailed status
gt polecat nuke <rig>/<name>              # Destroy (session, worktree, branch, bead)
gt polecat stale <rig>                    # Detect stale polecats
gt polecat gc <rig>                       # Garbage collect branches

# Death warrants (for stuck agents)
gt warrant file <target>                  # File warrant
gt warrant list                           # List pending warrants
gt warrant execute <target>               # Execute (terminate agent)
```

### 5. Inter-Agent Communication

```bash
# Inbox
gt mail inbox                             # Check inbox
gt mail peek                              # Preview first unread
gt mail read <id>                         # Read a message
gt mail thread <id>                       # View message thread

# Send
gt mail send <address>                    # Send a message
gt mail reply <id> [message]              # Reply to a message
gt nudge <session> "message"              # Synchronous message
gt broadcast "message"                    # Nudge all workers

# Manage
gt mail mark-read <id>                    # Mark as read
gt mail mark-unread <id>                  # Mark as unread
gt mail archive <id>                      # Archive messages
gt mail delete <id>                       # Delete messages
gt mail search "query"                    # Search messages
gt mail drain                             # Bulk-archive stale protocol messages
gt mail directory                         # List valid recipient addresses

# Groups, Channels, Queues
gt mail group list / create / show        # Mail groups
gt mail channel list / create / show      # Channels
gt mail queue list / create / show        # Queues
gt mail claim <queue>                     # Claim from queue
gt mail release <id>                      # Release claimed message

# Escalation
gt escalate "description" --severity high # Create escalation
gt escalate list                          # List open escalations
gt escalate ack <id>                      # Acknowledge
gt escalate close <id>                    # Close resolved
gt escalate stale                         # Re-escalate stale ones
```

**Addresses**: `rig/role` (e.g., "gastown/Toast"), `rig/crew/name`, `mayor/`, `--human`.

### 6. Merge Queue & Landing

```bash
# Polecat submits work
gt done                                   # Signal work ready for merge queue
gt done --pre-verified                    # Skip verification

# Merge queue operations
gt mq submit                              # Submit branch to merge queue
gt mq list <rig>                          # Show the merge queue
gt mq status <id>                         # Detailed MR status
gt mq next                                # Highest-priority MR
gt mq retry <rig> <mr-id>                 # Retry failed MR
gt mq reject <rig> <mr-id>               # Reject MR
gt mq post-merge <rig> <mr-id>           # Post-merge cleanup

# Integration branches (for epics)
gt mq integration create <epic>           # Create integration branch
gt mq integration land <epic>             # Merge to main
gt mq integration status <epic>           # Show status

# Refinery (merge queue processor)
gt refinery status                        # Show refinery status
gt refinery queue                         # Show queue
gt refinery ready                         # MRs ready for processing
gt refinery blocked                       # MRs blocked by open tasks
gt refinery start / stop / restart        # Manage lifecycle
gt refinery attach                        # Attach to session
```

### 7. Service Lifecycle

```bash
# All services
gt up                                     # Bring up all Gas Town services
gt down                                   # Stop all services
gt start                                  # Start Gas Town or crew workspace
gt shutdown                               # Shutdown with cleanup

# Daemon
gt daemon start / stop / status           # Manage daemon
gt daemon logs                            # View daemon logs

# Dolt database
gt dolt status                            # Show Dolt server status
gt dolt start / stop / restart            # Manage Dolt server
gt dolt sql                               # Open SQL shell
gt dolt init-rig <name>                   # Initialize rig database
gt dolt list                              # List rig databases
gt dolt logs                              # View server logs
gt dolt sync                              # Push to DoltHub remotes
gt dolt recover                           # Recover from read-only state
gt dolt rebase <db>                       # Surgical compaction
gt dolt flatten <db>                      # Flatten history (NUCLEAR)

# Rig lifecycle
gt rig start <rig>                        # Start witness and refinery
gt rig shutdown <rig>                     # Gracefully stop all rig agents
gt rig restart <rig>                      # Restart rig agents
gt rig park <rig>                         # Park (daemon won't auto-restart)
gt rig unpark <rig>                       # Unpark
gt rig dock <rig>                         # Dock (global persistent shutdown)
gt rig undock <rig>                       # Undock
```

### 8. Crew & Workspace

```bash
gt crew add <name>                        # Create crew workspace
gt crew start <name>                      # Start crew session
gt crew list                              # List workspaces with status
gt crew at <name>                         # Attach to session
gt crew stop <name>                       # Stop session
gt crew restart <name>                    # Kill and restart
gt crew status <name>                     # Detailed status
gt crew remove <name>                     # Remove workspace
gt crew rename <old> <new>                # Rename
gt crew refresh <name>                    # Context cycle with handoff mail
gt crew pristine                          # Sync with remote

# Session cycling
gt cycle next / prev                      # Cycle sessions in same group
gt town next / prev                       # Cycle town sessions (mayor/deacon)

# Memory
gt remember "insight"                     # Store persistent memory
gt remember "..." --type feedback         # Typed memory (feedback/project/user/reference)
gt memories                               # List memories
gt memories [search-term]                 # Search memories
gt forget <key>                           # Remove memory
```

## Command Quick-Reference by Group

### Work Management
| Command | Description |
|---------|-------------|
| `sling` | Assign work to an agent (THE dispatch command) |
| `unsling` | Remove work from agent's hook |
| `assign` | Create bead and hook to crew member |
| `close` | Close one or more beads |
| `done` | Signal work ready for merge queue |
| `convoy` | Track batches of work across rigs |
| `mq` / `mr` | Merge queue operations |
| `hook` / `work` | Show or attach work on a hook |
| `mol` / `molecule` | Agent molecule workflow commands |
| `formula` | Manage workflow formulas |
| `show` | Show details of a bead |
| `commit` | Git commit with automatic agent identity |
| `handoff` | Hand off to fresh session |
| `mountain` | Stage, label, and launch an epic |
| `ready` | Show work ready across town |
| `scheduler` | Manage dispatch scheduler |

### Agent Management
| Command | Description |
|---------|-------------|
| `agents` | List agent sessions |
| `polecat` / `polecats` | Manage polecats |
| `mayor` / `may` | Manage the Mayor |
| `deacon` / `dea` | Manage the Deacon |
| `dog` / `dogs` | Manage dogs (infra workers) |
| `witness` | Manage the Witness |
| `refinery` / `ref` | Manage the Refinery |
| `warrant` | Death warrants for stuck agents |
| `cycle` | Cycle between sessions in same group |
| `town` | Town-level operations (session cycling) |
| `boot` | Manage Boot (Deacon watchdog) |
| `session` | Manage polecat sessions |

### Communication
| Command | Description |
|---------|-------------|
| `mail` | Agent messaging system |
| `nudge` | Synchronous message to worker |
| `broadcast` | Nudge all workers |
| `escalate` | Escalation system (severity-based routing) |
| `peek` | View recent output from a session |
| `dnd` | Toggle Do Not Disturb |
| `notify` | Set notification level |

### Services
| Command | Description |
|---------|-------------|
| `up` / `down` | Bring up / stop all services |
| `start` / `shutdown` | Start / shutdown Gas Town |
| `daemon` | Manage the daemon |
| `dolt` | Manage the Dolt SQL server (20 subcommands) |
| `reaper` | Wisp and issue cleanup |
| `maintain` | Run full Dolt maintenance |
| `quota` | Account quota rotation |

### Workspace
| Command | Description |
|---------|-------------|
| `rig` | Manage rigs (16 subcommands) |
| `crew` | Manage crew workspaces |
| `worktree` | Cross-rig worktrees |
| `install` | Create a new Gas Town HQ |
| `init` | Initialize directory as a rig |
| `namepool` | Manage polecat name pools |

### Configuration
| Command | Description |
|---------|-------------|
| `config` | Manage configuration |
| `hooks` | Centralized hook management |
| `account` | Manage Codex accounts |
| `plugin` | Plugin management |
| `theme` | View or set tmux theme |
| `shell` | Manage shell integration |
| `remember` / `memories` / `forget` | Persistent memory system |
| `enable` / `disable` | Enable/disable Gas Town |
| `krc` | Key Record Chronicle (ephemeral data TTLs) |

### Diagnostics
| Command | Description |
|---------|-------------|
| `status` | Overall town status |
| `vitals` | Unified health dashboard |
| `health` | Comprehensive system health |
| `doctor` | Run health checks |
| `feed` | Real-time activity feed |
| `costs` | Show Codex session costs |
| `metrics` | Command usage statistics |
| `info` | Gas Town information |
| `whoami` | Current identity |
| `prime` | Output role context |
| `version` | Print version |
| `dashboard` | Web dashboard |

## Troubleshooting

### Agent stuck or unresponsive
```bash
gt peek <session>              # Check what it's doing
gt nudge <session> "status?"   # Try to wake it
gt vitals                      # Check health dashboard
gt polecat status <rig>/<name> # Detailed status
gt handoff                     # Hand off to fresh session
gt warrant file <agent>        # File death warrant
gt polecat nuke <rig>/<name>   # Last resort: destroy polecat
```

### Convoy not feeding next issue
```bash
gt convoy status <id>          # Check convoy state
gt convoy stranded             # Find stranded convoys
gt convoy check <id>           # Force check and auto-close
bd show <blocked-id>           # Check if next issue is blocked
```

### Merge queue stuck
```bash
gt mq list <rig>               # Show queue
gt mq status <id>              # Check specific MR
gt refinery status              # Check refinery health
gt refinery restart             # Restart refinery
gt mq retry <rig> <id>         # Retry failed MR
```

### Services down
```bash
gt health                      # Full health check
gt doctor                      # Run diagnostics
gt dolt status                 # Check Dolt server
gt dolt restart                # Restart Dolt
gt daemon status               # Check daemon
gt up                          # Bring everything up
```

### Orphaned processes
```bash
gt cleanup                     # Clean orphaned Codex processes
gt orphans                     # Find lost polecat work
gt deacon zombie-scan          # Find zombie processes
gt deacon cleanup-orphans      # Clean orphaned subagent processes
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GT_ROOT` / `GT_TOWN_ROOT` | Town root directory |
| `GT_SESSION` | Current agent session ID |
| `GT_ROLE` | Agent role (polecat, witness, etc.) |
| `GT_DOLT_PORT` | Dolt server port |
| `BEADS_DOLT_PORT` | Dolt port for beads CLI |
| `GT_COMMAND` | Override CLI binary name (default: `gt`) |
| `GT_SCOPE` | Agent scope (town or rig) |

## Key Paths

| Path | Purpose |
|------|---------|
| `~/gt/` | Default town root |
| `~/gt/<rig>/` | Rig directory (git repo) |
| `~/gt/<rig>/.beads/` | Beads data directory |
| `~/gt/.dolt-data/` | Centralized Dolt databases |
| `~/gt/<rig>/polecats/<name>/` | Polecat work directory |
| `~/gt/<rig>/crew/<name>/` | Crew workspace directory |
| `~/gt/<rig>/witness/` | Witness work directory |
| `~/gt/<rig>/refinery/` | Refinery work directory |

## References

For detailed command documentation with all flags and subcommands:
- `references/commands-work.md` — Work Management commands
- `references/commands-agents.md` — Agent Management commands
- `references/commands-comm.md` — Communication commands
- `references/commands-services.md` — Services commands
- `references/commands-workspace.md` — Workspace commands
- `references/commands-config-diag.md` — Configuration & Diagnostics commands
- `references/beads-cli.md` — bd/bv CLI reference
