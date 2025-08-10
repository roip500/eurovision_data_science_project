import json
import csv
import string
from collections import Counter, defaultdict

# --- Stopwords ---
stop_words = set("""
a about above after again against all am an and any are aren't as at be because been before being below between both 
but by can can't cannot could couldn't did didn't do does doesn't doing don't down during each few for from further 
had hadn't has hasn't have haven't having he he'd he'll he's her here here's hers herself him himself his how how's i 
i'd i'll i'm i've if in into is isn't it it's its itself let's me more most mustn't my myself no nor not of off on once 
only or other ought our ours ourselves out over own same shan't she she'd she'll she's should shouldn't so some such 
than that that's the their theirs them themselves then there there's these they they'd they'll they're they've this 
those through to too under until up very was wasn't we we'd we'll we're we've were weren't what what's when when's where 
where's which while who who's whom why why's with won't would wouldn't you you'd you'll you're you've your yours yourself 
yourselves
""".split())

# --- Load Eurovision data ---
with open('../basic_datasets/eurovision.json', 'r', encoding='utf-8') as f:
    contests = json.load(f)

all_words = []

for contest in contests:
    year = contest.get('year')
    if year == 1956:
        continue

    # --- Index contestants by ID ---
    contestants = {c['id']: c for c in contest.get('contestants', [])}

    # --- Track rounds ---
    rounds = contest.get('rounds', [])
    final_perfs = []
    semi_only_ids = set(contestants.keys())

    # Collect performances and determine round membership
    for rnd in rounds:
        round_name = rnd.get('name', '').lower()
        performances = rnd.get('performances', [])

        if 'final' in round_name:
            final_perfs = performances
            for p in performances:
                semi_only_ids.discard(p['contestantId'])

    # --- Process 3 lowest-placed finalists ---
    if final_perfs:
        # Sort performances by place descending (last place is highest number)
        sorted_final = sorted([p for p in final_perfs if 'place' in p and p['place']], key=lambda x: x['place'], reverse=True)
        bottom_finalists = sorted_final[:3]

        for perf in bottom_finalists:
            contestant = contestants.get(perf['contestantId'])
            if not contestant:
                continue

            lyrics_entries = contestant.get('lyrics', [])
            english_lyrics = next((lyr for lyr in lyrics_entries if 'English' in lyr.get('languages', [])), None)

            if english_lyrics:
                text = english_lyrics['content'].lower().translate(str.maketrans('', '', string.punctuation))
                words = [w for w in text.split() if w not in stop_words and len(w) > 2]
                all_words.extend(words)

    # --- Process non-finalists ---
    for cid in semi_only_ids:
        contestant = contestants.get(cid)
        if not contestant:
            continue

        lyrics_entries = contestant.get('lyrics', [])
        english_lyrics = next((lyr for lyr in lyrics_entries if 'English' in lyr.get('languages', [])), None)

        if english_lyrics:
            text = english_lyrics['content'].lower().translate(str.maketrans('', '', string.punctuation))
            words = [w for w in text.split() if w not in stop_words and len(w) > 2]
            all_words.extend(words)

# --- Count and save to JSON ---
word_counts = Counter(all_words)
top_words = word_counts.most_common(100)

with open('bottom_and_nonfinal_words.json', 'w', encoding='utf-8') as f:
    json.dump(dict(top_words), f, indent=4, ensure_ascii=False)

print(f"Saved word frequencies from bottom 3 and non-final songs to 'bottom_and_nonfinal_words.json'")
