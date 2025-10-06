# CHEZMOI.md

Comprehensive documentation about the chezmoi CLI tool and integration strategy for building a TUI wrapper.

## What is chezmoi?

chezmoi (pronounced "shay-mwa") is a command-line dotfile manager that helps users manage configuration files across multiple diverse machines securely. It's distributed as a single statically-linked binary, requires no root access, and supports cross-platform usage (Windows, macOS, Linux).

**Key Capabilities:**

- Template-based configuration for machine-specific differences
- Password manager integration (1Password, Bitwarden, LastPass, etc.)
- File encryption support (GPG/age)
- Script execution for complex setups
- Version control integration (Git)
- Secure handling of sensitive configuration data

## Core Concepts

### Directory Structure

**Source Directory** (`~/.local/share/chezmoi` by default):

- Git repository containing dotfiles and templates
- Files common to all machines
- Can be overridden with `--source` flag or config

**Destination Directory** (`$HOME` by default):

- Where dotfiles are actually applied
- Can be overridden with `--destination` flag

**Configuration File** (`~/.config/chezmoi/chezmoi.{toml,json,yaml}`):

- Machine-specific settings
- Supports TOML, JSON, JSONC, and YAML formats
- Contains template variables and chezmoi behavior settings

### State Management

chezmoi tracks three states:

1. **Source State**: Files in the source directory
2. **Target State**: What files should look like (after template processing)
3. **Destination State**: Current state of actual files in destination directory

### File Naming Conventions (Source State Attributes)

Files in the source directory use special prefixes and suffixes:

**Prefixes:**

- `dot_` - File starts with a dot (e.g., `dot_bashrc` → `.bashrc`)
- `executable_` - File has executable permissions
- `private_` - File removes group/world permissions
- `encrypted_` - File is encrypted
- `remove_` - File/directory should be removed from destination
- `create_` - Ensures file exists, creates if needed
- `run_` - Script to be executed
- `symlink_` - Creates a symlink

**Suffixes:**

- `.tmpl` - File contents are processed as a Go template
- `.literal` - Stops attribute parsing
- `.age`, `.asc` - Encryption suffixes (automatically stripped)

**Example:**

- Source: `dot_config/nvim/executable_private_init.vim.tmpl`
- Destination: `~/.config/nvim/init.vim` (executable, private, templated)

### Template System

chezmoi uses Go's `text/template` system with additional functions:

**Template Data Available:**

- `chezmoi` - Information about chezmoi environment (OS, arch, hostname, username, etc.)
- Custom variables from config file
- Password manager integrations
- Secret management functions

**Template Behavior:**

- Empty result removes the file/symlink
- Non-empty result becomes file content or symlink target
- Uses `missingkey=error` by default (fails on undefined variables)
- Whitespace is stripped for symlinks

## Command Categories

### Setup & Initialization

**`chezmoi init [repo]`**

- Initialize chezmoi on a new machine
- Clones repository if URL provided
- Can use GitHub username: `chezmoi init $GITHUB_USERNAME`
- Flags: `--apply` (apply after init), `--one-shot` (for temporary environments)

**`chezmoi doctor`**

- Diagnose common problems
- Checks for required tools and configuration issues

### Daily Operations

**`chezmoi add <file>`**

- Add a file to source directory
- Flags: `--template` (add as template), `--encrypt` (encrypt file)

**`chezmoi edit <file>`**

- Edit the source state version of a file
- Flags: `--apply` (auto-apply after edit), `--watch` (auto-apply on save)

**`chezmoi status [target]`**

- Show status of managed files (like `git status`)
- Two-column output:
  - Column 1: Difference between last written state and actual state
  - Column 2: Difference between actual state and target state
- Status codes: ` ` (no change), `A` (added), `D` (deleted), `M` (modified), `R` (run script)
- Flags: `--include`, `--exclude` (filter entry types), `--path-style`

**`chezmoi diff [target]`**

- Show differences between target and destination states
- Preview what `apply` will do

**`chezmoi apply [target]`**

- Apply changes from source to destination
- Updates dotfiles to match target state
- Flags: `--dry-run`, `--verbose`, `--interactive`, `--force`

**`chezmoi update`**

- Pull latest changes from git and apply
- Equivalent to: `chezmoi git pull && chezmoi apply`

### File Management

**`chezmoi managed [path]`**

- List all managed entries
- Supports JSON/YAML output: `--format json|yaml`
- Flags: `--include`, `--exclude` (filter types), `--tree` (tree view), `--path-style`
- Alias: `list`

**`chezmoi unmanaged [path]`**

- List unmanaged files in destination directory

**`chezmoi forget <target>`**

- Remove target from source state (doesn't delete from destination)

**`chezmoi remove <target>`** (or `destroy`)

- Permanently delete from source state AND destination

**`chezmoi re-add [targets]`**

- Re-add modified files (useful after manual edits)

### Git Integration

**`chezmoi cd`**

- Open subshell in source directory
- Allows direct git operations

**`chezmoi git <args>`**

- Run git commands in source directory
- Example: `chezmoi git status`, `chezmoi git commit -m "message"`

### Templates & Data

**`chezmoi data`**

- Print all available template data
- Flags: `--format json|yaml`
- Essential for debugging templates

**`chezmoi execute-template [template]`**

- Test and debug template syntax
- Can pass template via stdin or as argument

**`chezmoi cat <target>`**

- Print target contents of a file (after template processing)

### Path Utilities

**`chezmoi source-path <target>`**

- Show source path for a destination file

**`chezmoi target-path <source>`**

- Show destination path for a source file

### State Management

**`chezmoi state <subcommand>`**

- Manipulate persistent state
- Subcommands: `data`, `delete`, `dump`, `get`, `set`

**`chezmoi purge`**

- Remove all chezmoi configuration and data
- Nuclear option for complete reset

### Advanced Operations

**`chezmoi merge <target>`**

- Three-way merge between destination, source, and target states

**`chezmoi merge-all`**

- Perform three-way merge for all modified files

**`chezmoi archive`**

- Generate tar archive of target state

**`chezmoi dump`**

- Generate dump of target state
- Useful for debugging

**`chezmoi import <archive>`**

- Import archive into source state

## Global Flags (Available on All Commands)

**Output & Format:**

- `--format json|yaml` - JSON/YAML output (command-specific)
- `--color bool|auto` - Colorize output
- `--verbose, -v` - Verbose output
- `--debug` - Include debug information
- `--no-pager` - Disable pager
- `--output <path>, -o` - Write to file instead of stdout

**Directories:**

- `--source <path>, -S` - Override source directory
- `--destination <path>, -D` - Override destination directory
- `--config <path>, -c` - Override config file location
- `--cache <path>` - Override cache directory
- `--working-tree <path>, -W` - Set working tree directory

**Behavior:**

- `--dry-run, -n` - Don't make modifications
- `--force` - Make changes without prompting
- `--interactive` - Prompt for all changes
- `--keep-going, -k` - Continue after errors
- `--no-tty` - Don't attempt to get TTY for prompts

**Filtering:**

- `--include <types>, -i` - Include entry types (files, dirs, symlinks, scripts, etc.)
- `--exclude <types>, -x` - Exclude entry types

## Configuration File Structure

Example `~/.config/chezmoi/chezmoi.toml`:

```toml
[data]
    email = "user@example.com"
    name = "John Doe"

[git]
    autoCommit = true
    autoPush = true

[edit]
    command = "nvim"

[diff]
    pager = "delta"

sourceDir = "/custom/source/path"
```

## Common Workflows

### Initial Setup

```bash
# Initialize with existing repo
chezmoi init --apply https://github.com/username/dotfiles

# Or from GitHub username
chezmoi init --apply username
```

### Daily Development

```bash
# Check status
chezmoi status

# See what would change
chezmoi diff

# Apply changes
chezmoi apply

# Edit a file
chezmoi edit ~/.bashrc --apply

# Add a new file
chezmoi add ~/.vimrc
```

### Syncing Across Machines

```bash
# Pull and apply updates
chezmoi update

# Or manually
chezmoi git pull
chezmoi diff
chezmoi apply
```

### Working with Templates

```bash
# View template data
chezmoi data --format yaml

# Test a template
echo '{{ .chezmoi.hostname }}' | chezmoi execute-template

# Add file as template
chezmoi add --template ~/.gitconfig
```

## TUI Integration Strategy

### Design Principles

1. **Wrapper, Not Replacement**: The TUI should wrap chezmoi commands, not reimplement logic
2. **Leverage JSON Output**: Use `--format json` flags for structured data
3. **Subprocess Execution**: Call chezmoi as subprocess, parse output
4. **Visual Feedback**: Translate chezmoi's text output to visual widgets
5. **Progressive Disclosure**: Show common operations prominently, advanced features in menus

### Key Integration Points

#### 1. Status Dashboard

```python
# Get current status
subprocess.run(["chezmoi", "status"], capture_output=True)
# Parse two-column output to show:
# - Modified files (M*)
# - Added files (A*)
# - Deleted files (D*)
# - Scripts to run (R*)
```

#### 2. Managed Files List

```python
# Get all managed files in JSON
result = subprocess.run(
    ["chezmoi", "managed", "--format", "json"],
    capture_output=True
)
files = json.loads(result.stdout)
# Display in tree/list view with filtering
```

#### 3. Diff Viewer

```python
# Show diff for specific file
subprocess.run(["chezmoi", "diff", target_path])
# Display in split-pane or syntax-highlighted view
```

#### 4. Template Data Viewer

```python
# Get template data
result = subprocess.run(
    ["chezmoi", "data", "--format", "json"],
    capture_output=True
)
data = json.loads(result.stdout)
# Display as browsable tree structure
```

#### 5. Interactive Apply

```python
# Use --dry-run first to preview
subprocess.run(["chezmoi", "apply", "--dry-run", "--verbose"])
# Show preview, confirm with user
# Then execute actual apply
subprocess.run(["chezmoi", "apply"])
```

### Recommended TUI Screens

1. **Dashboard** - Status overview, quick stats
2. **File Browser** - Managed/unmanaged files, tree view
3. **Status View** - Detailed status like `chezmoi status`
4. **Diff View** - Visual diff for selected files
5. **Template Editor** - Edit with live template data preview
6. **Configuration** - Edit chezmoi config file
7. **Git Integration** - Git operations in source directory
8. **Setup Wizard** - Guide through `chezmoi init`

### Error Handling

- Capture stderr from chezmoi commands
- Parse error messages for user-friendly display
- Use `--debug` flag when needed for troubleshooting
- Check exit codes: 0 = success, non-zero = error

### Performance Considerations

- Cache `chezmoi managed` output, refresh on user action
- Use `--include`/`--exclude` flags to filter unnecessary data
- Lazy-load diffs (only compute when viewing)
- Consider async subprocess calls for long operations

### Testing Strategy

- Test against `chezmoi doctor` output
- Verify commands work with empty repository
- Test with various file types (encrypted, templated, symlinks)
- Handle missing chezmoi installation gracefully
- Test with different config formats (TOML, JSON, YAML)

## Important Notes for TUI Development

1. **Never Modify Source Directly**: Always use chezmoi commands, never edit `~/.local/share/chezmoi` directly
2. **Respect Dry-Run**: Always offer `--dry-run` preview before destructive operations
3. **Entry Types**: Files, directories, symlinks, and scripts have different behaviors
4. **Path Styles**: Support both absolute and relative path display
5. **Global Flags**: Allow users to set common flags (--verbose, --dry-run, etc.)
6. **Config Format Detection**: Support TOML, JSON, YAML auto-detection
7. **Template Errors**: Template parsing errors should be clearly displayed
8. **Git Integration**: Many users rely on auto-commit/auto-push features

## Resources

- Official Documentation: <https://www.chezmoi.io>
- GitHub Repository: <https://github.com/twpayne/chezmoi>
- Command Reference: <https://www.chezmoi.io/reference/commands/>
- Template Reference: <https://www.chezmoi.io/reference/templates/>
