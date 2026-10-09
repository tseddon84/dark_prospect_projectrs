import urllib.request
import urllib.parse
import json
import os
import re

API_URL = "https://darkprospects.us/rulesweb/api.php"
USER_AGENT = "AntigravityAgent/1.0"

def query_api(params):
    params['format'] = 'json'
    query_string = urllib.parse.urlencode(params)
    url = f"{API_URL}?{query_string}"
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error querying {url}: {e}")
        return {'query': {'pages': {}}}

def get_page_content(title):
    data = query_api({'action': 'query', 'prop': 'revisions', 'rvprop': 'content', 'titles': title})
    pages = data.get('query', {}).get('pages', {})
    for page_id, page_info in pages.items():
        if 'revisions' in page_info:
            rev = page_info['revisions'][0]
            if 'slots' in rev and 'main' in rev['slots']:
                return rev['slots']['main']['*']
            elif '*' in rev:
                return rev['*']
    return ""

def get_category_members(category_title):
    members = []
    cmcontinue = None
    while True:
        params = {'action': 'query', 'list': 'categorymembers', 'cmtitle': category_title, 'cmlimit': 'max'}
        if cmcontinue:
            params['cmcontinue'] = cmcontinue
        data = query_api(params)
        for member in data.get('query', {}).get('categorymembers', []):
            members.append(member['title'])
        if 'continue' in data and 'cmcontinue' in data['continue']:
            cmcontinue = data['continue']['cmcontinue']
        else:
            break
    return list(set(members))

def main():
    base_dir = "reference_materials"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Core Rulebook
    print("Fetching Changeling Rulebook...")
    content = get_page_content("Dark_Prospects_Changeling_Rulebook")
    with open(os.path.join(base_dir, "changeling_rulebook.md"), "w", encoding="utf-8") as f:
        f.write(content)
    print("Changeling Rulebook saved.")

    # 2. Powers
    print("Fetching Powers...")
    powers_content = get_page_content("Powers")
    power_titles = re.findall(r'\{\{PowerTemplate\|([^}]+)\}\}', powers_content)
    power_titles = list(set(power_titles))
    
    powers_dir = os.path.join(base_dir, "powers")
    os.makedirs(powers_dir, exist_ok=True)
    count = 0
    for pt in power_titles:
        pt = pt.strip()
        p_content = get_page_content(f"Power: {pt}")
        if not p_content: continue
        safe_title = "".join([c for c in pt if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
        with open(os.path.join(powers_dir, f"{safe_title}.md"), "w", encoding="utf-8") as f:
            f.write(f"# {pt}\n\n{p_content}")
        count += 1
    print(f"Saved {count} powers.")

    # 3. Rituals
    print("Fetching Ritual Types...")
    ritual_types_content = get_page_content("Ritual_Types")
    categories = re.findall(r'\[\[:?(Category:[^\]|]+)', ritual_types_content)
    
    rituals_dir = os.path.join(base_dir, "rituals")
    os.makedirs(rituals_dir, exist_ok=True)
    total_rituals = 0
    for cat in set(categories):
        print(f"Fetching rituals for {cat}...")
        cat_name = cat.replace("Category:", "").replace(" ", "_")
        cat_dir = os.path.join(rituals_dir, cat_name)
        os.makedirs(cat_dir, exist_ok=True)
        ritual_titles = get_category_members(cat)
        for rt in ritual_titles:
            r_content = get_page_content(rt)
            if not r_content: continue
            safe_title = "".join([c for c in rt if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
            safe_title = safe_title.replace("Ritual", "").strip("_")
            with open(os.path.join(cat_dir, f"{safe_title}.md"), "w", encoding="utf-8") as f:
                f.write(f"# {rt}\n\n{r_content}")
            total_rituals += 1
    print(f"Saved {total_rituals} rituals.")
    print("Scraping complete.")

if __name__ == "__main__":
    main()
