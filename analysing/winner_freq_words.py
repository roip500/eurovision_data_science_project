import csv
import json
from collections import Counter

# --- Load winning song data ---
word_counter = Counter()

with open('eurovision_song.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            year = int(row['year'])
            place = int(row['place']) if row['place'] else None
        except ValueError:
            continue

        if place == 1 and year != 1956:
            top_words = row.get('top_3_words', '')
            if top_words:
                words = [w.strip() for w in top_words.split(',') if w.strip()]
                word_counter.update(words)

# --- Save frequencies to JSON ---
output_dict = dict(word_counter.most_common())
with open('../datasets/winner_top_words.json', 'w', encoding='utf-8') as f:
    json.dump(output_dict, f, indent=4, ensure_ascii=False)

print(f"Saved frequencies of top 3 words from winning songs to 'winner_top_words.json'")
