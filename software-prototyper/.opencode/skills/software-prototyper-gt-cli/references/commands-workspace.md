# Workspace Commands

## rig — Manage rigs (16 subcommands)

### Core Operations
```bash
gt rig list                       # List all rigs in workspace
gt rig add <rig> --adopt --force  # Default: register/adopt a local rig into GT
gt rig add <rig> <git-url> --local-repo <path> --prefix <prefix>  # Optional: register a remote-bound rig
gt rig add <rig> file:///abs/path --prefix <prefix>  # Local source repo must use file:// URL
gt rig remove <rig>               # Remove from registry (no file deletion)
gt rig reset <rig>                # Reset state (handoff, mail, stale issues)
gt rig status <rig>               # Detailed rig status
```

### Rig Creation Modes
```bash
gt init                           # Initialize current directory as rig
gt rig add <rig> --adopt --force  # Default local-first path; does not require GitHub first
gt rig add <rig> <git-url> --local-repo <path> --prefix <prefix>  # Use only when binding rig to an existing remote repo
gt rig add <rig> file:///abs/path --prefix <prefix>  # Use when the source repo is local
```

- If the source repo is local, `<git-url>` must be `file:///abs/path`, not `/abs/path`.
- `--local-repo <path>` only enables local object reuse; it does not make a bare path a valid `<git-url>`.
- If `gt rig add` reports `invalid git URL "/abs/path"`, rewrite it as `file:///abs/path`.

### Lifecycle
```bash
gt rig start <rig>                # Start witness and refinery on patrol
gt rig boot <rig>                 # Start witness and refinery
gt rig restart <rig>              # Restart witness and refinery
gt rig reboot <rig>               # Restart witness and refinery
gt rig shutdown <rig>             # Gracefully stop all rig agents
gt rig stop <rig>                 # Stop rig (shutdown semantics)
```

### Park / Dock
```bash
gt rig park <rig>                 # Park rig (daemon won't auto-restart)
gt rig unpark <rig>               # Unpark rig
gt rig dock <rig>                 # Dock rig (global persistent shutdown)
gt rig undock <rig>               # Undock rig
```

### Configuration
```bash
gt rig config show <rig>          # Show effective config
gt rig config set <key> <val>     # Set config value
gt rig config unset <key>         # Remove config value
gt rig settings show <rig>        # Display all settings
gt rig settings set <key> <val>   # Set settings value
gt rig settings unset <key>       # Remove settings value
```

## crew — Manage crew workspaces (11 subcommands)

```bash
gt crew add <name>                # Create crew workspace
gt crew start [rig] [name...]     # Start crew session(s)
gt crew list [rig]                # List workspaces with status
gt crew at [name]                 # Attach to session (alias: attach)
gt crew stop [name...]            # Stop session(s)
gt crew restart [name...]         # Kill and restart session(s)
gt crew status [name]             # Detailed workspace status
gt crew remove <name...>          # Remove workspace(s)
gt crew rename <old> <new>        # Rename workspace
gt crew refresh <name>            # Context cycling with mail-to-self handoff
gt crew pristine [name]           # Sync crew workspaces with remote
```

## worktree — Cross-rig worktrees

```bash
gt worktree create <rig>          # Create worktree in another rig
gt worktree list                  # List cross-rig worktrees
gt worktree remove <worktree>     # Remove cross-rig worktree
```

## install — Create Gas Town HQ

```bash
gt install                        # Create new Gas Town HQ (workspace)
```

## init — Initialize rig

```bash
gt init                           # Initialize current directory as rig
```

## git-init — Initialize git for HQ

```bash
gt git-init                       # Initialize git repository for HQ
```

## namepool — Manage polecat name pools

```bash
gt namepool list                  # List available themes and names
gt namepool set <theme>           # Set namepool theme for rig
gt namepool add <name>            # Add custom name
gt namepool reset                 # Reset pool (release all names)
gt namepool create <theme>        # Create custom theme
gt namepool delete <theme>        # Delete custom theme
```
