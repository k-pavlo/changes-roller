#!/bin/bash
# Update pbr dependency version across oslo libraries
# This script updates the pbr requirement in both requirements.txt and pyproject.toml

set -e  # Exit on error

echo "Updating pbr dependency to 6.0.0..."

# Update in requirements.txt if it exists
if [ -f requirements.txt ]; then
    echo "  - Updating requirements.txt"
    sed -i 's/pbr>=.*$/pbr>=6.0.0/' requirements.txt
fi

# Update in pyproject.toml if it exists
if [ -f pyproject.toml ]; then
    echo "  - Updating pyproject.toml"
    sed -i 's/"pbr>=.*"/"pbr>=6.0.0"/' pyproject.toml
fi

# Update in test-requirements.txt if it exists
if [ -f test-requirements.txt ]; then
    echo "  - Updating test-requirements.txt"
    sed -i 's/pbr>=.*$/pbr>=6.0.0/' test-requirements.txt
fi

echo "Update complete!"
exit 0
