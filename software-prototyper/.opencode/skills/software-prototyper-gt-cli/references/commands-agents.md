# Agent Management Commands

## agents — List agent sessions

```bash
gt agents list                    # List sessions (no popup)
gt agents menu                    # Interactive popup menu
gt agents check                   # Check identity collisions
gt agents fix                     # Fix identity collisions
```

## polecat — Manage worker agents

Aliases: `polecats`

```bash
gt polecat list [rig]                     # List polecats in rig
gt polecat status <rig>/<name>            # Detailed polecat status
gt polecat remove <rig>/<name>            # Remove polecat
gt polecat nuke <rig>/<name>              # Destroy (session, worktree, branch, bead)
gt polecat nuke <rig> --all               # Nuke all polecats in rig
gt polecat gc <rig>                       # Garbage collect stale branches
gt polecat stale <rig>                    # Detect stale polecats
gt polecat git-state <rig>/<name>         # Show git state for pre-kill verification
gt polecat check-recovery <rig>/<name>    # Check if recovery needed vs safe to nuke
gt polecat prune <rig>                    # Prune stale branches (local + remote)
gt polecat pool-init <rig>                # Initialize persistent polecat pool
```

### Identity management
```bash
gt polecat identity add <rig> [name]      # Create identity bead
gt polecat identity list <rig>            # List identities
gt polecat identity show <rig> <name>     # Show detailed identity info
gt polecat identity rename <rig> <old> <new>  # Rename identity
gt polecat identity remove <rig> <name>   # Remove identity
```

## mayor — Manage the Mayor

Aliases: `may`

```bash
gt mayor start                    # Start Mayor session
gt mayor stop                     # Stop Mayor
gt mayor attach                   # Attach to session
gt mayor status                   # Check status
gt mayor restart                  # Restart Mayor
gt mayor acp                      # Run in headless mode (Agent Control Protocol)
```

## deacon — Manage the Deacon

Aliases: `dea`

```bash
gt deacon start                   # Start Deacon session
gt deacon stop                    # Stop Deacon
gt deacon attach                  # Attach to session
gt deacon status                  # Check status
gt deacon restart                 # Restart Deacon
gt deacon heartbeat [action]      # Manage heartbeat
gt deacon health-check <agent>    # Send health check ping
gt deacon force-kill <agent>      # Force-kill unresponsive agent
gt deacon health-state            # Show health state for all agents
gt deacon stale-hooks             # Find and unhook stale beads
gt deacon pause                   # Pause patrol actions
gt deacon resume                  # Resume patrol actions
gt deacon cleanup-orphans         # Clean orphaned subagent processes
gt deacon zombie-scan             # Find zombie Claude processes
gt deacon redispatch <bead-id>    # Re-dispatch recovered bead
gt deacon redispatch-state        # Show re-dispatch state
gt deacon feed-stranded           # Detect and feed stranded convoys
gt deacon feed-stranded-state     # Show feed-stranded state
```

## dog — Manage infrastructure workers

Aliases: `dogs`

```bash
gt dog list                       # List all dogs
gt dog add <name>                 # Create new dog
gt dog remove <name>              # Remove dog
gt dog call <name>                # Wake idle dog for work
gt dog done <name>                # Mark done, return to idle
gt dog clear <name>               # Reset stuck dog to idle
gt dog status <name>              # Detailed dog status
gt dog dispatch <name> <plugin>   # Dispatch plugin to dog
gt dog health-check               # Check dog health
```

## witness — Manage the Witness

```bash
gt witness start                  # Start witness
gt witness stop                   # Stop witness
gt witness status                 # Show status
gt witness attach                 # Attach to session
gt witness restart                # Restart witness
```

## refinery — Manage the Refinery

Aliases: `ref`

```bash
gt refinery start                 # Start refinery
gt refinery stop                  # Stop refinery
gt refinery status                # Show status
gt refinery queue                 # Show merge queue
gt refinery attach                # Attach to session
gt refinery restart               # Restart refinery
gt refinery claim <mr-id>         # Claim MR for processing
gt refinery release <mr-id>       # Release claimed MR
gt refinery ready                 # List MRs ready for processing
gt refinery unclaimed             # List unclaimed MRs
gt refinery blocked               # List MRs blocked by open tasks
```

## warrant — Death warrants for stuck agents

```bash
gt warrant file <target>          # File death warrant
gt warrant list                   # List pending warrants
gt warrant execute <target>       # Execute warrant (terminate agent)
```

## cycle — Cycle between sessions

```bash
gt cycle next                     # Switch to next session in group
gt cycle prev                     # Switch to previous session in group
```

Session groups: Town (Mayor/Deacon), Crew (same rig), Rig ops (Witness/Refinery/Polecats).

## town — Town-level operations

```bash
gt town next                      # Switch to next town session (mayor/deacon)
gt town prev                      # Switch to previous town session
```

## boot — Manage Boot (Deacon watchdog)

```bash
gt boot status                    # Show Boot status
gt boot spawn                     # Spawn Boot for triage
gt boot triage                    # Run triage directly
```

## session — Manage polecat sessions

```bash
gt session start <name>           # Start polecat session
gt session stop <name>            # Stop session
gt session attach <name>          # Attach to session (alias: at)
gt session list                   # List sessions
gt session capture <name>         # Capture recent output
gt session restart <name>         # Restart session
gt session status <name>          # Session status details
gt session check <name>           # Check session health
```

## Other Agent Commands

```bash
gt signal ...                     # Claude Code hook signal handlers
gt callbacks process              # Process pending callbacks
gt role show                      # Show current role
gt role list                      # List all roles
gt role home <role>               # Show home directory for role
gt role env                       # Print export statements
gt role def <role>                # Display role definition
gt role detect                    # Detect current role
```
