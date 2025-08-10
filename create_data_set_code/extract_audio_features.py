import os
import re
import json
import glob
import subprocess
import pandas as pd

def clean_filename(s):
    return re.sub(r'[\\/*?:"<>|]', "", s)

def download_audio():
    print("🎧 Starting audio download...")
    audio_dir = '../audio'
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    contestants = pd.read_csv('../basic_datasets/contestants.csv')
    # No year filter here — downloads all years

    import youtube_dl

    for i, r in contestants.iterrows():
        destination_dir = os.path.join(audio_dir, str(r['year']))
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        youtube_url = r['youtube_url']
        if pd.isna(youtube_url) or youtube_url.strip() == "":
            continue

        fn = '{}_{}_{}'.format(
            clean_filename(r['to_country']),
            clean_filename(r['song']),
            clean_filename(r['performer'])
        )
        fp = os.path.join(destination_dir, fn)

        if not os.path.exists(fp + '.mp3'):
            ydl_opts = {
                'outtmpl': fp + '.%(ext)s',
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'nocheckcertificate': True,  # NOT recommended unless necessary

            }
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])
                print(f"Downloaded {fp}.mp3")
            except Exception as e:
                print(f"Failed to download {youtube_url}: {e}")
        else:
            print(f"{fp}.mp3 already exists")

def extract_audio_features():
    print("🎵 Starting audio features extraction...")
    from shutil import which

    if which('streaming_extractor_music') is None:
        raise FileNotFoundError('Essentia\'s streaming_extractor_music is not found in PATH')

    files = glob.glob('audio/**/*.mp3', recursive=True)
    for f in files:
        output_path = os.path.splitext(f)[0] + '.json'
        if not os.path.exists(output_path):
            print(f'Extracting audio features from {f}')
            subprocess.call(['streaming_extractor_music', f, output_path])
        else:
            print(f'Audio features already extracted for {f}')

def json_features_to_csv(output_csv='audio_features.csv'):
    print("📝 Converting JSON audio features to CSV...")
    json_files = glob.glob('audio/**/*.json', recursive=True)
    features_list = []

    for jf in json_files:
        try:
            with open(jf, 'r') as f:
                data = json.load(f)

            # Extract year and country from path or filename
            parts = jf.split(os.sep)
            year = parts[1] if len(parts) > 1 else None  # audio/2023/filename.json

            filename = os.path.splitext(os.path.basename(jf))[0]

            # Parse filename convention: country_song_performer
            parts_name = filename.split('_')
            country = parts_name[0] if len(parts_name) > 0 else None
            song = parts_name[1] if len(parts_name) > 1 else None
            performer = parts_name[2] if len(parts_name) > 2 else None

            features = {
                "year": int(year) if year and year.isdigit() else None,
                "country": country,
                "song": song,
                "performer": performer,
                "tempo": data.get('rhythm', {}).get('bpm', None),
                "danceability": data.get('rhythm', {}).get('danceability', None),
                "energy": data.get('lowlevel', {}).get('average_loudness', None),
                "loudness": data.get('lowlevel', {}).get('average_loudness', None),
                "spectral_centroid": data.get('lowlevel', {}).get('spectral_centroid', None),
            }
            features_list.append(features)
        except Exception as e:
            print(f"Failed to parse {jf}: {e}")

    df_audio = pd.DataFrame(features_list)
    df_audio.to_csv(output_csv, index=False)
    print(f"✅ Audio features saved to {output_csv}")
    return df_audio

def main():
    # Step 1: Download all audio
    download_audio()

    # Step 2: Extract audio features with Essentia
    extract_audio_features()

    # Step 3: Convert JSON features to CSV
    audio_df = json_features_to_csv()

    # Step 4: Load contestants and merge with audio features
    dataset_folder = "basic_datasets"
    contestants_file = os.path.join(dataset_folder, "contestants.csv")
    contestants = pd.read_csv(contestants_file)
    df = contestants[contestants["place_final"].notna()]

    df = pd.merge(
        df,
        audio_df,
        left_on=["year", "to_country", "song", "performer"],
        right_on=["year", "country", "song", "performer"],
        how="left"
    )

    # Save the merged dataframe
    df.to_csv("contestants_with_audio_features.csv", index=False)
    print("✅ Final dataset with audio features saved to contestants_with_audio_features.csv")

if __name__ == "__main__":
    main()
