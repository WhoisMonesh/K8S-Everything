#!/usr/bin/env python3
"""Fix Mermaid diagrams for GitHub compatibility."""
import os
import re

def fix_mermaid_syntax(content):
    """Fix common Mermaid syntax issues for GitHub compatibility."""
    lines = content.split('\n')
    fixed_lines = []
    in_mermaid = False
    
    for i, line in enumerate(lines):
        if line.strip() == '```mermaid':
            in_mermaid = True
            fixed_lines.append(line)
            continue
        elif line.strip() == '```' and in_mermaid:
            in_mermaid = False
            fixed_lines.append(line)
            continue
        
        if not in_mermaid:
            fixed_lines.append(line)
            continue
        
        # Fix \n newlines -> <br/>
        if '\\n' in line:
            line = line.replace('\\n', '<br/>')
        
        # Fix </br> -> <br/>
        if '</br>' in line:
            line = line.replace('</br>', '<br/>')
        
        # Fix &#40; and &#41; -> use quoted labels
        if '&#40;' in line or '&#41;' in line:
            # This needs more complex handling - skip for now
            pass
        
        # Fix unquoted subgraph names
        if 'subgraph' in line.lower() and not line.strip().startswith('%%'):
            # Match: subgraph Name or subgraph Name [Label]
            match = re.match(r'^(\s*subgraph\s+)([A-Za-z0-9_\-]+)(.*)', line)
            if match:
                prefix = match.group(1)
                name = match.group(2)
                rest = match.group(3)
                # Don't quote if already quoted or if it's a special char
                if not name.startswith('"') and name not in ['{', '[', '(']:
                    line = f'{prefix}"{name}"{rest}'
        
        # Fix unquoted parentheses in bracket labels
        # Match: [text(parentheses)] or [(text)]
        if '[' in line and ']' in line:
            # Find bracket contents
            bracket_match = re.search(r'\[([^\]]*)\]', line)
            if bracket_match:
                inner = bracket_match.group(1)
                # Check for unquoted parentheses
                if '(' in inner and '"' not in inner:
                    # Quote the entire bracket content
                    new_inner = f'"{inner}"'
                    line = line[:bracket_match.start()] + '[' + new_inner + ']' + line[bracket_match.end():]
        
        # Fix unquoted parentheses in parentheses labels (database symbols)
        # Match: [(text)] or (text)
        if re.search(r'\(\([^)]*\)\)', line):
            # Database symbol: ((text))
            match = re.search(r'\(\(([^\)]*)\)\)', line)
            if match:
                inner = match.group(1)
                if '"' not in inner:
                    new_inner = f'"{inner}"'
                    line = line[:match.start()] + '((' + new_inner + '))' + line[match.end():]
        
        # Fix unquoted edge labels with /
        # Match: --text/ or --text-- with /
        if '--' in line and '/' in line:
            # Look for edge labels
            match = re.search(r'--([^"]*?/[^"]*?)--', line)
            if match and '"' not in match.group(1):
                label = match.group(1)
                new_label = f'"{label}"'
                line = line[:match.start()] + '--' + new_label + '--' + line[match.end():]
        
        # Fix ampersands not in entity form
        if '&' in line and '&amp;' not in line and '&#' not in line:
            # Only fix in labels, not in URLs
            if '-->' in line or '[' in line or '(' in line:
                # Don't fix in HTTP URLs
                if 'http' not in line:
                    line = line.replace('&', '&amp;')
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def process_file(filepath):
    """Process a single markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content = fix_mermaid_syntax(content)
        
        if fixed_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False

def main():
    repo_path = '.'
    files_fixed = 0
    
    for root, dirs, files in os.walk(repo_path):
        if '.git' in root:
            continue
        
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                if process_file(filepath):
                    files_fixed += 1
                    print(f"Fixed: {filepath}")
    
    print(f"\nTotal files fixed: {files_fixed}")

if __name__ == '__main__':
    main()
