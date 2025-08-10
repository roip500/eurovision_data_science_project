import csv
import json
from collections import Counter

# --- Load data from CSV ---
word_counter = Counter()

with open('eurovision_song.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            year = int(row['year'])
            place_str = row['place']
            place = int(place_str) if place_str else None
        except ValueError:
            continue

        # Skip 1956
        if year == 1956:
            continue

        # Check if song is bottom 3 or didn't make final (place is None)
        if (place is not None and place >= 22) or (place is None):
            top_words = row.get('top_3_words', '')
            if top_words:
                words = [w.strip() for w in top_words.split(',') if w.strip()]
                word_counter.update(words)

# --- Save result to JSON ---
output_dict = dict(word_counter.most_common())
with open('../datasets/loser_top_words.json', 'w', encoding='utf-8') as f:
    json.dump(output_dict, f, indent=4, ensure_ascii=False)

print(f"Saved frequencies of top 3 words from last-place or non-finalist songs to 'loser_top_words.json'")
