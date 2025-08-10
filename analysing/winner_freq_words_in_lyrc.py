import csv
import json
import string
from collections import Counter

# --- Basic English stopwords list (no downloads needed) ---
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

# --- Storage for all words ---
all_words = []

# --- Load songs from CSV ---
with open('eurovision_songs_final.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            year = int(row['year'])
            place = int(row['place']) if row['place'] else None
        except ValueError:
            continue

        # Filter only top 3 songs (excluding 1956)
        if place and place <= 3 and year != 1956:
            lyrics = row['lyrics_english']
            if lyrics and lyrics != "Not available in English":
                # Normalize text: lowercase, remove punctuation
                text = lyrics.lower().translate(str.maketrans('', '', string.punctuation))
                words = text.split()
                # Filter out stopwords and short words
                words = [word for word in words if word not in stop_words and len(word) > 2]
                all_words.extend(words)

# --- Count word frequencies ---
word_counts = Counter(all_words)
top_words = word_counts.most_common(100)

# --- Save to JSON ---
output_dict = dict(top_words)
with open('top_words.json', 'w', encoding='utf-8') as f:
    json.dump(output_dict, f, indent=4, ensure_ascii=False)

print(f"Top {len(top_words)} word frequencies saved to 'top_words.json'")
