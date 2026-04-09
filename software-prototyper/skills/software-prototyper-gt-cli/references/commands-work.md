# Work Management Commands

## sling — Assign work to an agent

THE unified work dispatch command. Handles polecats, crew, mayor, dogs.

```bash
gt sling <bead-or-formula> [target]
```

### Target Resolution
```bash
gt sling gt-abc                          # Self (current agent)
gt sling gt-abc <rig>                    # Auto-spawn polecat in rig
gt sling gt-abc <rig>/<polecat>          # Specific polecat
gt sling gt-abc <rig> --crew <name>      # Crew member in rig
gt sling gt-abc mayor                    # Mayor
gt sling gt-abc deacon/dogs              # Auto-dispatch to idle dog
gt sling gt-abc deacon/dogs/<name>       # Specific dog
```

### Flags
| Flag | Description |
|------|-------------|
| `-s, --subject` | Context subject for the work |
| `-m, --message` | Context message for the work |
| `-a, --args` | Natural language instructions for the executor |
| `--formula` | Formula to apply (default: mol-polecat-work for polecats) |
| `--var` | Formula variable (key=value), repeatable |
| `--on` | Apply formula to existing bead (implies wisp scaffolding) |
| `--force` | Force spawn even if polecat has unread mail |
| `--create` | Create polecat if it doesn't exist |
| `--account` | Claude Code account handle to use |
| `--agent` | Override agent/runtime (claude, gemini, codex, custom) |
| `--crew` | Target a crew member in specified rig |
| `--no-convoy` | Skip auto-convoy creation |
| `--owned` | Mark auto-convoy as caller-managed lifecycle |
| `--no-merge` | Skip merge queue on completion |
| `--merge` | Merge strategy: direct, mr (default), local |
| `--base-branch` | Override base branch for polecat worktree |
| `--ralph` | Enable Ralph Wiggum loop mode |
| `--hook-raw-bead` | Hook raw bead without default formula (expert) |
| `--max-concurrent` | Limit concurrent polecat spawns in batch mode |
| `--stdin` | Read --message/--args from stdin |
| `-n, --dry-run` | Show what would be done |
| `--no-boot` | Skip rig boot after polecat spawn |

### Subcommands
- `respawn-reset` — Reset the respawn counter for a bead

### Examples
```bash
gt sling gt-abc gastown                            # Basic dispatch
gt sling gt-abc gt-def gt-ghi gastown              # Batch dispatch
gt sling gt-abc gastown --merge=direct             # Push directly to main
gt sling gt-abc gastown -a "patch release"         # With instructions
gt sling mol-release mayor/                        # Formula to Mayor
gt sling shiny --on gt-abc crew                    # Formula on existing bead
echo "review security" | gt sling gt-abc gastown --stdin
```

**Flow**: acquire flock → check bead → burn stale mols → spawn polecat → auto-convoy → cook formula → hook bead → start session.

## unsling — Remove work from hook

```bash
gt unsling <bead-id>
```

## assign — Create bead and hook to crew

```bash
gt assign --title "Fix bug" <crew-name>
```

## close — Close beads

```bash
gt close <id1> <id2> ...
```

## done — Signal work ready for merge queue

```bash
gt done                           # Submit MR and self-clean
gt done --pre-verified            # Skip verification step
```

## commit — Git commit with agent identity

```bash
gt commit [flags] [-- git-commit-args...]
```

Passes through to git commit with automatic agent identity injection.

## show — Show bead details

```bash
gt show <bead-id> [flags]         # Delegates to bd show
```

## convoy — Track batches of work

```bash
gt convoy create <name> [issues...]       # Create convoy
gt convoy stage <epic-id | task-id... | convoy-id>  # Analyze deps, compute waves
gt convoy launch <convoy-id | epic-id>    # Launch (dispatch Wave 1)
gt convoy status [convoy-id]              # Show status
gt convoy list                            # List convoys (dashboard)
gt convoy check [convoy-id]               # Check and auto-close
gt convoy stranded                        # Find stranded convoys
gt convoy add <convoy-id> <bead-id>       # Add issues
gt convoy close <convoy-id>               # Close convoy
gt convoy land <convoy-id>                # Land owned convoy (cleanup + close)
```

Flag: `-i, --interactive` — Interactive tree view

## mq — Merge queue operations

Alias: `mr`

```bash
gt mq submit                              # Submit branch to merge queue
gt mq list <rig>                          # Show the merge queue
gt mq status <id>                         # Detailed MR status
gt mq next                                # Highest-priority MR
gt mq retry <rig> <mr-id>                 # Retry failed MR
gt mq reject <rig> <mr-id-or-branch>      # Reject MR
gt mq post-merge <rig> <mr-id>            # Post-merge cleanup

# Integration branches
gt mq integration create <epic-id>        # Create integration branch
gt mq integration land <epic-id>          # Merge to main
gt mq integration status <epic-id>        # Show status
```

## hook — Show or attach work

Aliases: `work`

```bash
gt hook                                   # Show what's on your hook
gt hook <bead-id>                         # Attach work to your hook
gt hook <bead-id> <target>                # Attach work to another agent
gt hook status                            # Show hook status
gt hook show <agent>                      # Show agent's hook (compact)
gt hook attach <bead-id>                  # Attach work to hook
gt hook detach                            # Detach work from hook
gt hook clear                             # Clear hook
```

Flags: `-s, --subject`, `-m, --message`, `-f, --force`, `--json`, `-n, --dry-run`

## mol / molecule — Workflow step commands

```bash
gt mol current                            # Show what to work on
gt mol progress <mol-id>                  # Show step progress
gt mol status                             # Show hook/attachment status
gt mol attach <bead-id>                   # Attach molecule to pinned bead
gt mol attach-from-mail <msg-id>          # Attach from mail
gt mol attachment                         # Show attachment status
gt mol detach <bead-id>                   # Detach molecule
gt mol burn <mol-id>                      # Burn molecule (no record)
gt mol squash <mol-id>                    # Compress to digest
gt mol dag <mol-id>                       # Visualize dependency DAG
gt mol step done                          # Complete step, auto-continue
gt mol step await-signal                  # Wait for activity feed signal
```

## formula — Manage workflow formulas

```bash
gt formula list                           # List available formulas
gt formula show <name>                    # Display formula details
gt formula run <name>                     # Execute a formula
gt formula create <name>                  # Create new formula template
```

## Other Work Commands

```bash
gt handoff                                # Hand off to fresh session
gt resume                                 # Check for handoff messages
gt ready                                  # Show work ready across town
gt release <bead-id>                      # Release stuck in_progress → pending
gt compact                                # Compact expired wisps
gt orphans                                # Find lost polecat work
gt trail                                  # Show recent agent activity
gt trail commits / beads / hooks          # Filtered views
gt cat <bead-id>                          # Display bead content
gt bead show <id>                         # Show bead details
gt bead move <id> <rig>                   # Move bead to different rig
gt scheduler status                       # Scheduler state
gt scheduler list                         # Scheduled beads
gt scheduler pause / resume               # Pause/resume dispatch
gt scheduler run                          # Manual trigger dispatch
gt mountain eat <epic-id>                 # Activate Mountain-Eater
gt mountain status / pause / resume / cancel
gt synthesis start / status / close <convoy-id>
gt cleanup                                # Clean orphaned Claude processes
gt prune-branches                         # Remove stale polecat branches
gt wl join / browse / post / claim / done / sync  # Wasteland federation
```
