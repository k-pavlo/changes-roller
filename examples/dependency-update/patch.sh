#!/bin/bash
# Example patch script: Update a Python dependency

set -e

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "No requirements.txt found, skipping"
    exit 0
fi

# Update the hacking library version
sed -i 's/hacking>=3.0.0,<4.0.0/hacking>=4.0.0,<5.0.0/' requirements.txt

echo "Updated hacking library version in requirements.txt"
