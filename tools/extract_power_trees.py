import urllib.request
import json
import re

splats = ['Vampire_Rules', 'Werewolf_Rules', 'Wraith_Rules', 'Fera_Rules', 'Changeling_Rules', 'Mortal_Rules']
output_content = "# Power Trees Reference\n\nThis document compiles the power structures (Disciplines, Gifts, Arts, etc.) for all major splats to analyze power valuation across the game.\n\n"

for splat in splats:
    print(f"Fetching {splat}...")
    req = urllib.request.Request(f'https://darkprospects.us/rulesweb/api.php?action=query&prop=revisions&rvprop=content&titles={splat}&format=json', headers={'User-Agent': 'Mozilla/5.0'})
    try:
        data = json.loads(urllib.request.urlopen(req).read().decode())
        pages = data.get('query', {}).get('pages', {})
        text = list(pages.values())[0]['revisions'][0]['*']
        
        # Regex to capture from the Powers header to the next major header (or EOF)
        match = re.search(r"('''''\[\[#Power_Format_and_Descriptor_Line_Tags\|[^\]]+\]\]'''''|'''''\[\[#Power_Format_and_Descriptor_Line_Tags\|.*?Powers.*?'''''|==='''''\[\[#Power_Format.*?)(?=\n==+'''''|\n===''\'\'|\Z)", text, re.IGNORECASE | re.DOTALL)
        
        if match:
            output_content += f"## {splat.replace('_', ' ')}\n\n"
            output_content += match.group(1).strip() + "\n\n---\n\n"
        else:
            # Fallback for Mortal Rules which might be different
            match_fallback = re.search(r"('''''Mortal Powers.*?'''''.*?)(?=\n==+'''''|\n===''\'\'|\Z)", text, re.IGNORECASE | re.DOTALL)
            if match_fallback:
                output_content += f"## {splat.replace('_', ' ')}\n\n"
                output_content += match_fallback.group(1).strip() + "\n\n---\n\n"
            else:
                print(f"  Warning: Could not find powers section for {splat}")
                
    except Exception as e:
        print(f"Error processing {splat}: {e}")

with open('reference_materials/power_trees_reference.md', 'w', encoding='utf-8') as f:
    f.write(output_content)

print("Done. Saved to reference_materials/power_trees_reference.md")
