import json
import pandas as pd

def load_json_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_data_for_excel(eurovision_data):
    rows = []
    for contest in eurovision_data:
        year = contest.get('year')
        contestants = {c['id']: c for c in contest.get('contestants', [])}
        rounds = contest.get('rounds', [])
        final_round = next((r for r in rounds if r['name'].lower() == 'final'), None)

        performances = {}
        if final_round:
            for perf in final_round.get('performances', []):
                performances[perf['contestantId']] = perf

        for contestant_id, contestant in contestants.items():
            perf = performances.get(contestant_id, {})
            rows.append({
                'Year': year,
                'Country': contestant.get('country'),
                'Artist': contestant.get('artist'),
                'Song': contestant.get('song'),
                'Running Order': perf.get('running'),
                'Place': perf.get('place'),
                'Points': next((s['points'] for s in perf.get('scores', []) if s['name'] == 'total'), None),
                'Dances': perf.get('dances'),
                'Tone': contestant.get('tone'),
                'BPM': contestant.get('bpm'),
                'Stage Director': contestant.get('stageDirector'),
            })
    return rows

def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Saved data to {filename}")

if __name__ == '__main__':
    eurovision_data = load_json_file('../basic_datasets/eurovision.json')
    data_rows = extract_data_for_excel(eurovision_data)
    save_to_excel(data_rows, 'eurovision_data.xlsx')
