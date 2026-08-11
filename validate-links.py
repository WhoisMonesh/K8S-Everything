#!/usr/bin/env python3
"""Validate all internal markdown links in the K8S-Everything repository."""

import os
import re
from pathlib import Path

REPO_ROOT = Path("/Users/whoism/verc/K8S")
TOTAL_LINKS = 0
BROKEN_LINKS = []

def resolve_link(source_file, link_target):
    """Check if a link target resolves to an existing file."""
    source_dir = source_file.parent
    
    # Handle absolute paths from repo root
    if link_target.startswith("/"):
        return REPO_ROOT / link_target[1:]
    
    # Handle relative paths
    resolved = (source_dir / link_target).resolve()
    
    # Check if it exists (file or directory)
    if resolved.exists():
        return resolved
    
    # Check without .md extension
    if not resolved.suffix:
        md_path = resolved.with_suffix('.md')
        if md_path.exists():
            return md_path
    
    # Check if it's a directory with README
    if resolved.is_dir():
        readme = resolved / "README.md"
        if readme.exists():
            return readme
    
    return None

def remove_code_blocks(content):
    """Remove code blocks from content to avoid false positives."""
    # Remove inline code (backticks)
    content = re.sub(r'`[^`]+`', '', content)
    # Remove fenced code blocks
    content = re.sub(r'```[\s\S]*?```', '', content)
    return content

def validate_links_in_file(filepath):
    """Validate all markdown links in a file."""
    global TOTAL_LINKS
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove code blocks to avoid false positives
    cleaned_content = remove_code_blocks(content)
    
    # Find all markdown links: [text](url)
    link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
    matches = link_pattern.findall(cleaned_content)
    
    for text, url in matches:
        # Skip external links, anchors, and special links
        if url.startswith('http://') or url.startswith('https://') or url.startswith('#'):
            continue
        
        # Skip badge/shield URLs
        if 'img.shields.io' in url:
            continue
        
        TOTAL_LINKS += 1
        
        # Clean up URL - remove anchors
        clean_url = url.split('#')[0] if '#' in url else url
        
        if not clean_url:
            continue
        
        # Try to resolve the link
        resolved = resolve_link(filepath, clean_url)
        
        if resolved is None:
            BROKEN_LINKS.append((str(filepath.relative_to(REPO_ROOT)), text, url))

def main():
    """Walk through all markdown files and validate links."""
    print("Validating internal links in K8S-Everything repository...")
    print(f"Repository root: {REPO_ROOT}")
    print()
    
    # Walk through all markdown files
    for root, dirs, files in os.walk(REPO_ROOT):
        # Skip .git directory
        if '.git' in root:
            continue
        
        for file in files:
            if file.endswith('.md'):
                filepath = Path(root) / file
                validate_links_in_file(filepath)
    
    print(f"Total internal links validated: {TOTAL_LINKS}")
    print(f"Broken links found: {len(BROKEN_LINKS)}")
    print()
    
    if BROKEN_LINKS:
        print("BROKEN LINKS:")
        print("-" * 80)
        for source, text, url in BROKEN_LINKS:
            print(f"  Source: {source}")
            print(f"  Text: {text}")
            print(f"  URL: {url}")
            print()
    else:
        print("All internal links are valid!")
    
    print("Validation complete.")

if __name__ == "__main__":
    main()
