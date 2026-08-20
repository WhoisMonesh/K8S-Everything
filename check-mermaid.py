#!/usr/bin/env python3
"""Check all Mermaid diagrams for GitHub compatibility issues."""
import os
import re

def check_mermaid_syntax(content, filename):
    """Check a single Mermaid diagram for syntax issues."""
    issues = []
    
    # Check for problematic characters
    if '&#40;' in content or '&#41;' in content:
        issues.append("  HTML entities &#40;/&#41; - use quoted labels instead")
    
    if '\\n' in content:
        issues.append("  \\n newlines - use <br/> instead")
    
    if '</br>' in content:
        issues.append("  </br> tags - use <br/> instead")
    
    # Check for unquoted parentheses in node labels
    # Match ( but not inside quotes or already in brackets
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Skip subgraph lines and comments
        if line.strip().startswith('%%') or 'subgraph' in line.lower():
            continue
        
        # Check for unquoted parentheses in node definitions
        # Look for patterns like A(text with parens) without quotes
        if re.search(r'\[[^\]]*\([^\)]*\)[^\]]*\]', line):
            # Already in square brackets - check if inner has quotes
            inner = re.search(r'\[([^\]]*)\]', line)
            if inner and '(' in inner.group(1) and '"' not in inner.group(1):
                issues.append(f"  Line {i+1}: Unquoted parentheses in bracket label: {line.strip()[:80]}")
        
        # Check for parentheses in non-bracket labels
        # Like A(text) or A(text with parens)
        if re.search(r'[A-Za-z0-9_]+\([^)]*\)', line):
            # Check if it's not a subgraph or edge label
            if 'subgraph' not in line and '-->' not in line and '---' not in line:
                if '"' not in line:
                    issues.append(f"  Line {i+1}: Unquoted parentheses: {line.strip()[:80]}")
    
    # Check for unquoted subgraph names
    for i, line in enumerate(lines):
        if 'subgraph' in line.lower():
            # Check if subgraph name is quoted
            match = re.search(r'subgraph\s+"([^"]+)"', line)
            if not match:
                # Check if it has a name that needs quoting
                match2 = re.search(r'subgraph\s+(\S+)', line)
                if match2 and match2.group(1) not in ['{', '[', '(']:
                    name = match2.group(1)
                    if not name.startswith('"'):
                        issues.append(f"  Line {i+1}: Unquoted subgraph name '{name}' - wrap in quotes")
    
    # Check for unquoted edge labels with special chars
    for i, line in enumerate(lines):
        # Look for edge labels like --/text/ or --text--
        if '--' in line and '/' in line:
            # Check for unquoted labels with slashes
            match = re.search(r'--([^"]*?)/([^"]*?)--', line)
            if match:
                issues.append(f"  Line {i+1}: Unquoted edge label with '/' - wrap in quotes")
    
    # Check for angle brackets in labels (HTML-like)
    for i, line in enumerate(lines):
        if '<' in line and '>' in line:
            # Check if it's a valid HTML tag or problematic
            if re.search(r'<[a-z]+>', line) and '<br/>' not in line and '</br>' not in line:
                # Check for tags like <pod> that would be interpreted as HTML
                tag_match = re.search(r'<([a-z]+)>', line)
                if tag_match and tag_match.group(1) not in ['br']:
                    issues.append(f"  Line {i+1}: HTML-like tag <{tag_match.group(1)}> - use quotes or &lt;/&gt;")
    
    # Check for ampersands not in entity form
    for i, line in enumerate(lines):
        if '&' in line and '&amp;' not in line and '&#' not in line:
            # Check if it's in a label or text
            if '-->' in line or '[' in line or '(' in line:
                issues.append(f"  Line {i+1}: Unescaped '&' - use &amp;")
    
    return issues

def extract_mermaid_blocks(content, filename):
    """Extract all mermaid blocks from markdown content."""
    blocks = []
    in_mermaid = False
    current_block = []
    block_start = 0
    
    for i, line in enumerate(content.split('\n')):
        if line.strip() == '```mermaid':
            in_mermaid = True
            current_block = []
            block_start = i + 1
        elif line.strip() == '```' and in_mermaid:
            in_mermaid = False
            blocks.append({
                'block': '\n'.join(current_block),
                'start_line': block_start,
                'filename': filename
            })
        elif in_mermaid:
            current_block.append(line)
    
    return blocks

def main():
    repo_path = '.'
    total_blocks = 0
    total_issues = 0
    files_with_issues = []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip .git directory
        if '.git' in root:
            continue
        
        for file in files:
            if file.endswith('.md'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    blocks = extract_mermaid_blocks(content, filepath)
                    
                    for block_info in blocks:
                        total_blocks += 1
                        issues = check_mermaid_syntax(block_info['block'], filepath)
                        
                        if issues:
                            total_issues += len(issues)
                            files_with_issues.append({
                                'file': filepath,
                                'line': block_info['start_line'],
                                'issues': issues
                            })
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    # Print results
    print(f"Mermaid Diagram Check Complete")
    print(f"=" * 60)
    print(f"Total diagrams checked: {total_blocks}")
    print(f"Total issues found: {total_issues}")
    print(f"Files with issues: {len(files_with_issues)}")
    print()
    
    if files_with_issues:
        print("Issues Found:")
        print("-" * 60)
        for file_info in files_with_issues:
            print(f"\n{file_info['file']}:{file_info['line']}")
            for issue in file_info['issues']:
                print(issue)
    else:
        print("No issues found! All diagrams should render correctly on GitHub.")
    
    return len(files_with_issues)

if __name__ == '__main__':
    exit(main())
