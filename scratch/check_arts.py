import codecs
import re

text = codecs.open('scratch/arts_raw.txt', 'r', 'utf-16le').read()
arts = re.findall(r'<span class="treename">([^<]+)</span>(.*?)(?=<div class="tree">|\Z)', text, re.DOTALL)
for name, content in arts:
    print(f"{name}: {content.count('treepower')} powers")
