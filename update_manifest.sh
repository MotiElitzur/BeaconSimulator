#!/bin/bash

# Prompt the user to enter an Extension Id
read -p "Enter Extension Id: " extension_id
# extension_id="gighmmpiobklfepjocnamgkkbiglidom"

# Define the base directory, prepending with the home directory symbol (~)
base_dir="$HOME/Library/Application Support/Google/Chrome"

# Find directories containing the Extension Id
find "$base_dir" -type d -name "*$extension_id*" | while read directory; do
    # echo "Searching in directory: $directory"
    # Search for manifest.json files within these directories and subdirectories
    find "$directory" -type f -name "manifest.json" | while read manifest_file; do
        echo "Found manifest.json: $manifest_file"
        # Use jq to update the update_url field if it exists and add override_update_url field
        jq 'if .update_url then .update_url = "https://127.0.0.1" | .override_update_url = true else . end' "$manifest_file" > temp.json && mv temp.json "$manifest_file"
        echo "Updated update_url and added override_update_url in: $manifest_file"
    done
done