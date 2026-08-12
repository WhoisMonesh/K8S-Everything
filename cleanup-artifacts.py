#!/usr/bin/env python3
"""Remove shell artifacts (EOF and echo lines) from markdown files."""

import os
import re
from pathlib import Path

REPO_ROOT = Path("/Users/whoism/verc/K8S")

def remove_shell_artifacts(filepath):
    """Remove EOF and echo lines from a markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Remove lines that match common shell artifacts
    # Pattern: lines that are just "EOF" or "echo "... written""
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        stripped = line.strip()
        # Skip lines that are just "EOF"
        if stripped == 'EOF':
            continue
        # Skip lines that are echo commands writing files
        if stripped.startswith('echo "') and 'written' in stripped:
            continue
        # Skip empty lines at the end of file
        cleaned_lines.append(line)
    
    # Remove trailing empty lines
    while cleaned_lines and cleaned_lines[-1].strip() == '':
        cleaned_lines.pop()
    
    cleaned_content = '\n'.join(cleaned_lines)
    
    if cleaned_content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        return True
    return False

def main():
    """Find and clean all affected markdown files."""
    print("Removing shell artifacts from markdown files...")
    
    # Find all affected files
    affected_files = []
    for root, dirs, files in os.walk(REPO_ROOT):
        if '.git' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                filepath = Path(root) / file
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'EOF' in content or 'echo ".*written"' in content:
                    affected_files.append(filepath)
    
    print(f"Found {len(affected_files)} affected files")
    
    cleaned_count = 0
    for filepath in affected_files:
        if remove_shell_artifacts(filepath):
            cleaned_count += 1
            print(f"  Cleaned: {filepath.relative_to(REPO_ROOT)}")
    
    print(f"\nCleaned {cleaned_count} files")

if __name__ == "__main__":
    main()
