# VHS documentation: https://github.com/charmbracelet/vhs
# This tape script demonstrates the basic changes-roller workflow
# Using the real oslo-dependency-update example

Output basic-workflow.gif

Set Theme "Catppuccin Mocha"
Set FontSize 14
Set Width 1200
Set Height 800
Set Padding 20

# Introduction
Type "# changes-roller demo: Update dependencies across multiple repos"
Enter
Sleep 1s

Type "# We have an example that updates pbr across oslo libraries"
Enter
Sleep 1s

# Show the configuration
Type "cat examples/oslo-dependency-update/series.ini | head -25"
Enter
Sleep 4s

# Show the patch script
Type "# Here's the patch script that will run in each repo:"
Enter
Sleep 500ms

Type "cat examples/oslo-dependency-update/patch.sh"
Enter
Sleep 3s

# Run with dry-run
Type "# Let's test with dry-run first (safe, no changes):"
Enter
Sleep 500ms

Type "cd examples/oslo-dependency-update/ && roller create --config-file series.ini --dry-run"
Enter
Sleep 4s

# Explain what happens
Type "# In production, this would:"
Enter
Sleep 500ms

Type "# 1. Clone 6 oslo repos in parallel"
Enter
Sleep 500ms

Type "# 2. Run patch.sh in each repo"
Enter
Sleep 500ms

Type "# 3. Run tests (tox -e py310)"
Enter
Sleep 500ms

Type "# 4. Create commits with templated messages"
Enter
Sleep 500ms

Type "# 5. Optionally submit to Gerrit for review"
Enter
Sleep 2s
