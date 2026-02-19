# Demo Generation

This directory contains VHS scripts for generating demo GIFs and videos that showcase changes-roller functionality.

## What is VHS?

[VHS](https://github.com/charmbracelet/vhs) is a tool for generating terminal recordings as GIFs, MP4s, or WebM files. It uses a simple scripting language (`.tape` files) to define what commands to type and when.

## Prerequisites

Install VHS using one of these methods:

### macOS

```bash
brew install vhs
```

### Linux

```bash
# Using Go
go install github.com/charmbracelet/vhs@latest

# Or download binary from releases
# https://github.com/charmbracelet/vhs/releases
```

### Verify Installation

```bash
vhs --version
```

## Generate Demo GIF

To generate the basic workflow demo:

```bash
# Navigate to the demos directory
cd demos

# Run VHS with the tape script
vhs basic-workflow.tape
```

This will create `basic-workflow.gif` in the current directory.

## Available Demos

### basic-workflow.tape

Demonstrates the core changes-roller workflow using the oslo-dependency-update example:

1. Show the configuration file (series.ini)
2. Show the patch script (patch.sh)
3. Run with dry-run mode (safe, no changes)
4. Explain what the tool does in production

**Output**: `basic-workflow.gif` (~1-2 MB)
**Duration**: ~25-30 seconds
**Note**: Uses real example from `examples/oslo-dependency-update/`

## Customize Demos

Edit the `.tape` files to customize the demos. Common customizations:

### Change Theme

```tape
Set Theme "Dracula"  # or "Nord", "Monokai", etc.
```

### Adjust Terminal Size

```tape
Set Width 1400
Set Height 800
```

### Modify Timing

```tape
Sleep 5s    # Wait 5 seconds
Sleep 500ms # Wait 500 milliseconds
```

### Change Font Size

```tape
Set FontSize 16
```

## Output Formats

VHS can generate different formats by changing the `Output` directive:

```tape
# GIF (recommended for README)
Output demo.gif

# MP4 (for high quality video)
Output demo.mp4

# WebM (for web embedding)
Output demo.webm
```

## Tips for Good Demos

1. **Keep it short**: 15-30 seconds is ideal
2. **Clear commands**: Add comment lines to explain what's happening
3. **Adequate sleep times**: Give viewers time to read output
4. **Consistent theme**: Use professional-looking color schemes
5. **Test first**: Run the actual commands to ensure they work

## Troubleshooting

### VHS not found

Ensure VHS is installed and in your PATH:

```bash
which vhs
```

### Permission denied

Make sure the tape file is readable:

```bash
chmod 644 basic-workflow.tape
```

### Demo too large

Reduce terminal size or duration:

```tape
Set Width 1000
Set Height 600
# Reduce sleep times
```

### Commands not working

Test commands manually first, then update the tape script to match working commands.

## Contributing New Demos

To add a new demo:

1. Create a new `.tape` file (e.g., `multi-branch-demo.tape`)
2. Follow the structure of existing demos
3. Test the demo: `vhs your-demo.tape`
4. Add entry to this README under "Available Demos"
5. Update `.gitignore` if needed

## Resources

- [VHS GitHub Repository](https://github.com/charmbracelet/vhs)
- [VHS Documentation](https://github.com/charmbracelet/vhs#vhs)
- [Available Themes](https://github.com/charmbracelet/vhs#themes)
- [Command Reference](https://github.com/charmbracelet/vhs#command-reference)
