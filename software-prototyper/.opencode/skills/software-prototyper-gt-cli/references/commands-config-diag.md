# Configuration & Diagnostics Commands

## Configuration

### config — Manage Gas Town configuration

```bash
gt config set <key> <value>       # Set configuration value
gt config get <key>               # Get configuration value
gt config agent list              # List all agents (built-in + custom)
gt config agent get <name>        # Show agent configuration
gt config agent set <name> <cmd>  # Set custom agent command
gt config agent remove <name>     # Remove custom agent
gt config cost-tier [tier]        # Get or set cost optimization tier
gt config default-agent [name]    # Get or set default agent
gt config agent-email-domain [domain]  # Get or set agent email domain
```

### hooks — Centralized hook management

```bash
gt hooks list                     # Show all managed settings.json locations
gt hooks sync                     # Regenerate all .claude/settings.json files
gt hooks init                     # Bootstrap from existing settings.json
gt hooks diff [target]            # Show what sync would change
gt hooks base                     # Edit shared base hook config
gt hooks override <target>        # Edit overrides for role or rig
gt hooks install <hook-name>      # Install hook from registry
gt hooks registry                 # List available hooks
gt hooks scan                     # Scan workspace for existing hooks
```

Config structure: Base (`~/.gt/hooks-base.json`) → Role → Rig+Role overrides.

### account — Manage Claude Code accounts

```bash
gt account list                   # List registered accounts
gt account add <name>             # Add new account
gt account default <name>         # Set default account
gt account info                   # Show current account info (alias: status)
gt account switch <name>          # Switch to different account
```

### plugin — Plugin management

```bash
gt plugin list                    # List discovered plugins
gt plugin show <name>             # Show plugin details
gt plugin run <name>              # Trigger plugin execution
gt plugin sync                    # Sync from source repo
gt plugin history <name>          # Show execution history
gt plugin dispatch <name>         # Dispatch plugin to a dog
```

### theme — View or set themes

```bash
gt theme                          # View or set tmux theme for rig
gt theme apply                    # Apply theme to running sessions
gt theme cli                      # View or set CLI color scheme (dark/light/auto)
gt theme themes                   # List available themes
```

### shell — Shell integration

```bash
gt shell install                  # Install shell integration
gt shell remove                   # Remove shell integration
gt shell status                   # Show integration status
```

### Memory System

```bash
gt remember "insight"                     # Store persistent memory
gt remember "insight" --type feedback     # Typed: feedback/project/user/reference
gt remember "insight" --key my-key        # Explicit key slug
gt memories                               # List all memories
gt memories [search-term]                 # Search memories
gt memories --type feedback               # Filter by type
gt forget <key>                           # Remove a stored memory
```

### Other Configuration

```bash
gt tap                            # Claude Code hook handlers
gt tap list                       # List available tap handlers
gt issue set <id>                 # Set current issue (tmux status line)
gt issue clear                    # Clear current issue
gt issue show                     # Show current issue
gt enable                         # Enable Gas Town system-wide
gt disable                        # Disable Gas Town system-wide
gt uninstall                      # Remove Gas Town from system
gt krc stats                      # KRC ephemeral data statistics
gt krc expire                     # Remove expired events
gt krc ttl                        # View/modify TTL config
gt krc set-ttl <pattern> <dur>    # Set TTL for event type
gt krc reset-ttl                  # Reset TTL to defaults
gt krc decay                      # Forensic value decay report
gt krc schedule                   # Auto-prune scheduling state
```

---

## Diagnostics

### status — Overall town status

```bash
gt status                         # Show overall town status
```

### vitals — Health dashboard

```bash
gt vitals                         # Show unified health dashboard
```

### health — System health

```bash
gt health                         # Comprehensive system health
```

### doctor — Health checks

```bash
gt doctor                         # Run health checks on workspace
```

### feed — Activity feed

```bash
gt feed                           # Real-time activity feed of gt events
```

### activity — Activity events

```bash
gt activity emit <event>          # Emit an activity event
```

### costs — Session costs

```bash
gt costs                          # Show costs for Claude sessions
gt costs record                   # Record session cost (Stop hook)
gt costs digest                   # Aggregate into daily digest
```

### metrics — Usage statistics

```bash
gt metrics                        # Show command usage statistics
```

### log — Town activity log

```bash
gt log                            # View town activity log
gt log crash                      # Record crash event
```

### Other Diagnostics

```bash
gt info                           # Gas Town information and what's new
gt whoami                         # Current identity for mail commands
gt prime                          # Output role context for current directory
gt version                        # Print version information
gt dashboard                      # Start convoy tracking web dashboard
gt patrol digest                  # Aggregate patrol digests
gt patrol new                     # Create new patrol
gt patrol report                  # Generate patrol report
gt audit <actor>                  # Query work history by actor
gt seance                         # Talk to predecessor sessions
gt checkpoint write               # Write session checkpoint
gt checkpoint read                # Read checkpoint
gt checkpoint clear               # Clear checkpoint
gt upgrade                        # Run post-install migration
gt stale                          # Check if gt binary is stale
gt heartbeat                      # Update agent heartbeat state
gt thanks                         # Thank human contributors
gt completion bash/zsh/fish       # Generate autocompletion script
```
