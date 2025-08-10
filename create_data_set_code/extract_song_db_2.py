import json
import csv
import string
from collections import Counter


def load_json_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_placements_and_running(rounds):
    final_round = next((r for r in rounds if r['name'].lower() == 'final'), None)
    placements = {}
    running_orders = {}
    dancers_count = {}   # <-- NEW

    if final_round:
        for perf in final_round.get('performances', []):
            contestant_id = perf['contestantId']
            placements[contestant_id] = {
                'place': perf.get('place'),
                'points': next((s['points'] for s in perf.get('scores', []) if s['name'] == 'total'), None)
            }
            running_orders[contestant_id] = perf.get('running')
            dancers_count[contestant_id] = perf.get('dances')  # <-- NEW

    return placements, running_orders, dancers_count


def get_lyrics_data(lyrics):
    if not lyrics:
        return 'Unknown', 'Unknown', 'Not available', 'Not available in English'

    main_language = lyrics[0].get('languages', ['Unknown'])[0]
    all_languages = ', '.join(lyrics[0].get('languages', []))
    lyrics_original = lyrics[0].get('content', '').replace('\n', ' ')[:300] + "..."

    english_lyrics = next(
        (lyr for lyr in lyrics if 'English' in lyr.get('languages', [])),
        None
    )
    lyrics_english = english_lyrics['content'].replace('\n', ' ')[:300] + "..." if english_lyrics else "Not available in English"

    return main_language, all_languages, lyrics_original, lyrics_english


def get_top_3_words(lyrics):
    if lyrics == "Not available in English":
        return ''

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

    text = lyrics.lower().translate(str.maketrans('', '', string.punctuation))
    words = [word for word in text.split() if word not in stop_words and len(word) > 2]
    top_words = [w for w, _ in Counter(words).most_common(3)]
    return ', '.join(top_words)


def process_song(contestant_id, contestant, placements, running_orders, dancers_count, country_codes, year):
    main_language, all_languages, lyrics_original, lyrics_english = get_lyrics_data(contestant.get('lyrics', []))
    country_code = contestant.get('country', '??')
    country_name = country_codes.get(country_code, country_code)

    return {
        'year': year,
        'country': country_name,
        'artist': contestant.get('artist'),
        'song': contestant.get('song'),
        'all_languages': all_languages,
        'main_language': main_language,
        'lyrics_original': lyrics_original,
        'lyrics_english': lyrics_english,
        'bpm': contestant.get('bpm'),
        'tone': contestant.get('tone'),
        'dancers': dancers_count.get(contestant_id),
        'stage_director': contestant.get('stageDirector'),
        'place': placements.get(contestant_id, {}).get('place'),
        'points': placements.get(contestant_id, {}).get('points'),
        'running_order': running_orders.get(contestant_id),
        'top_3_words': get_top_3_words(lyrics_english)
    }


def main():
    eurovision_data = load_json_file('../basic_datasets/eurovision.json')
    country_codes = load_json_file('../basic_datasets/countries.json')

    songs_data = []

    for contest in eurovision_data:
        year = contest.get('year')
        rounds = contest.get('rounds', [])
        contestants = {c['id']: c for c in contest.get('contestants', [])}
        placements, running_orders, dancers_count = extract_placements_and_running(rounds)

        for contestant_id, contestant in contestants.items():
            song_entry = process_song(
                contestant_id, contestant, placements, running_orders, dancers_count, country_codes, year
            )
            songs_data.append(song_entry)

    save_to_csv(songs_data, '../datasets/eurovision_dataset_2.csv')
    print(f"Saved {len(songs_data)} songs to eurovision_song_2.csv")


def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


if __name__ == '__main__':
    main()
