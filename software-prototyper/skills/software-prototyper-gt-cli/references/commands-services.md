# Services Commands

## up / down — Service lifecycle

```bash
gt up                             # Bring up all Gas Town services
gt down                           # Stop all Gas Town services
gt start                          # Start Gas Town or crew workspace
gt start crew <name>              # Start crew workspace
gt shutdown                       # Shutdown Gas Town with cleanup
```

## daemon — Manage the Gas Town daemon

```bash
gt daemon start                   # Start the daemon
gt daemon stop                    # Stop the daemon
gt daemon status                  # Show daemon status
gt daemon logs                    # View daemon logs
gt daemon run                     # Run in foreground (internal)
gt daemon autostart               # Configure launchd/systemd auto-restart
gt daemon rotate                  # Rotate daemon log files
gt daemon clear-backoff <agent>   # Clear crash loop backoff for agent
```

## dolt — Manage the Dolt SQL server (20 subcommands)

### Server Management
```bash
gt dolt status                    # Show Dolt server status
gt dolt start                     # Start the Dolt server
gt dolt stop                      # Stop the Dolt server
gt dolt restart                   # Restart (kills imposters first)
gt dolt kill-imposters            # Kill servers hijacking this port
gt dolt logs                      # View Dolt server logs
gt dolt dump                      # Dump goroutine stacks for debugging
gt dolt sql                       # Open Dolt SQL shell
```

### Database Management
```bash
gt dolt init-rig <name>           # Initialize a new rig database
gt dolt list                      # List available rig databases
gt dolt migrate                   # Migrate to centralized data directory
gt dolt fix-metadata              # Update metadata.json in all .beads dirs
gt dolt recover                   # Detect and recover from read-only state
gt dolt cleanup                   # Remove orphaned databases from .dolt-data/
gt dolt rollback [backup-dir]     # Restore .beads from migration backup
gt dolt sync                      # Push databases to DoltHub remotes
gt dolt migrate-wisps             # Migrate agent beads from issues to wisps
gt dolt init                      # Initialize and repair workspace config
```

### Maintenance
```bash
gt dolt rebase <database>         # Surgical compaction: squash old, keep recent
gt dolt flatten <database>        # Flatten history to single commit (NUCLEAR)
```

## reaper — Wisp and issue cleanup (6 subcommands)

Dog-callable helpers for the mol-dog-reaper formula.

```bash
gt reaper databases               # List databases available for reaping
gt reaper scan --db=<name>        # Scan database for reaper candidates
gt reaper reap --db=<name>        # Close stale wisps past max-age
gt reaper purge --db=<name>       # Delete old closed wisps and mail
gt reaper auto-close --db=<name>  # Close stale issues past stale-age
gt reaper run                     # Run full reaper cycle across all databases
```

## maintain — Dolt maintenance

```bash
gt maintain                       # Run full Dolt maintenance (reap + flatten + gc)
```

## quota — Account quota rotation (5 subcommands)

```bash
gt quota status                   # Show account quota status
gt quota scan                     # Detect rate-limited sessions
gt quota rotate                   # Swap blocked sessions to available accounts
gt quota clear [handle...]        # Mark account(s) as available again
gt quota watch                    # Monitor and rotate proactively before hard 429
```
