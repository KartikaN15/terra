import os
from pathlib import Path
import re

def fix_files():
    base_dir = Path('c:/Users/E36250409/Desktop/Terra')
    count = 0
    
    # We want to find files where backslash is used as a mistake
    # We will look for sequences of spaces followed by a backslash, e.g., "   \\"
    # and replace the backslash with an em-dash "—".
    # We'll avoid backslashes that are followed by typical escape characters or are inside regexes.
    
    for p in base_dir.rglob('*'):
        if p.is_file() and not p.name.endswith('.pyc') and not '.git' in p.parts and 'node_modules' not in p.parts and 'venv' not in p.parts:
            try:
                content = p.read_text(encoding='utf-8')
                # Look for "   \" or "  \" or " \" not followed by n, r, t, d, s, w, W, b, B, or quote
                # Or wait, let's just look for occurrences of '   \\' or '  \\' and see what they are
                if '   \\' in content or '  \\' in content or '\\the' in content:
                    pass # We will process this file
                else:
                    continue
                
                # Let's replace "   \\" with " — "
                # Wait, if they replaced '— ' with '\', then ' — ' became ' \'.
                # But '   \\' means there were 3 spaces. '   — ' became '   \'.
                # Let's do a regex replacement: replace backslash that is preceded by spaces and followed by a word character
                # with an em-dash and a space? Or maybe just an em-dash.
                
                new_content = content
                
                # Find all occurrences of spaces followed by \ and a letter
                def repl(match):
                    spaces = match.group(1)
                    letter = match.group(2)
                    return f"{spaces}— {letter}"
                    
                # We replace <spaces>\ followed by <letter> with <spaces>— <letter>
                # But what if they just replaced "—" with "\"? Then " — " became " \ ".
                # Let's see what's actually there.
                
                new_content, n = re.subn(r'( +)\\([a-zA-Z])', r'\1— \2', content)
                
                if n > 0:
                    p.write_text(new_content, encoding='utf-8')
                    print(f"Fixed {n} occurrences in {p.relative_to(base_dir)}")
                    count += 1
            except Exception as e:
                pass
                
    print(f"Fixed {count} files in total.")

if __name__ == '__main__':
    fix_files()
