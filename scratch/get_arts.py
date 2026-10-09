import urllib.request, json, re
req = urllib.request.Request('https://darkprospects.us/rulesweb/api.php?action=query&prop=revisions&rvprop=content&titles=Changeling_Rules&format=json', headers={'User-Agent': 'Mozilla/5.0'})
data = json.loads(urllib.request.urlopen(req).read().decode())
text = list(data['query']['pages'].values())[0]['revisions'][0]['*']
arts = re.findall(r'<span class="treename">([^<]+)</span>', text)
print("Arts found:", arts)
