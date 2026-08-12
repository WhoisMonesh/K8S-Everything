#!/usr/bin/env python3
"""Fix all Mermaid diagram syntax issues in markdown files."""

import os
import re
from pathlib import Path

REPO_ROOT = Path("/Users/whoism/verc/K8S")

def fix_mermaid_newlines(content):
    """Replace \\n with <br/> inside Mermaid node labels."""
    # This regex matches content inside [] or () or {} that contains \n
    # We need to be careful not to replace \n in code blocks
    
    lines = content.split('\n')
    in_mermaid = False
    fixed_lines = []
    
    for line in lines:
        # Track if we're inside a mermaid block
        if line.strip() == '```mermaid':
            in_mermaid = True
            fixed_lines.append(line)
            continue
        elif line.strip() == '```' and in_mermaid:
            in_mermaid = False
            fixed_lines.append(line)
            continue
        
        if in_mermaid:
            # Fix \n inside node labels [..] or (..)
            # Replace \n with <br/> but only inside node shapes
            line = re.sub(r'\[([^\]]*?)\\n([^\]]*?)\]', r'[\1<br/>\2]', line)
            line = re.sub(r'\(([^\)]*?)\\n([^\)]*?)\)', r'(\1<br/>\2)', line)
            
            # Handle multiple \n in same label
            line = re.sub(r'\[([^\]]*?)\\n([^\]]*?)\\n([^\]]*?)\]', r'[\1<br/>\2<br/>\3]', line)
            line = re.sub(r'\(([^\)]*?)\\n([^\)]*?)\\n([^\)]*?)\)', r'(\1<br/>\2<br/>\3)', line)
            
            # Fix unescaped & in node labels (but not in &amp; already)
            line = re.sub(r'&(?![a-zA-Z])', '&amp;', line)
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_mermaid_in_file(filepath):
    """Fix all Mermaid issues in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = fix_mermaid_newlines(content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all Mermaid diagrams in all markdown files."""
    print("Fixing Mermaid diagram syntax issues...")
    
    fixed_count = 0
    for root, dirs, files in os.walk(REPO_ROOT):
        if '.git' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                filepath = Path(root) / file
                if fix_mermaid_in_file(filepath):
                    fixed_count += 1
                    print(f"  Fixed: {filepath.relative_to(REPO_ROOT)}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()
