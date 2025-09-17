from create_data_set_code import analyze_song_meaning as asm, extract_song_db_2, extract_song_db_1, lgtbq_artist_list, merge_datasets
import pandas as pd

def create_dataset():
    # extract_song_db_1.main()  # mute this command if dataset1 exists - takes long
    print("Creating dataset2...")
    extract_song_db_2.main()
    print("Creating sexuality dataset...")
    # lgtbq_artist_list.main()
    print("merging")
    merge_datasets.merge_datasets()

    print("cleaning...")
    # ------------------ clean code

    # things to edit out: all rows that the year arent between 1956 and 2025
    # columns to remove: every column that contains drop, youtube_url, youtube_url.1, lyrics.1, lyrics

    # Step 2: Load merged dataset (adjust file name if different)
    df = pd.read_csv("datasets/final_merged.csv")

    # Step 3: Ensure year is numeric
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # Step 4: Keep only rows where Year is between 1956 and 2025
    df = df[(df["year"] >= 1956) & (df["year"] <= 2025)]

    # Step 5: Remove duplicate rows based on year, country, artist, and song
    df = df.drop_duplicates(subset=["year", "country", "artist", "song"], keep="first")

    # Step 6: Drop unwanted columns
    cols_to_drop = [col for col in df.columns if
                    "drop" in str(col).lower() or
                    "youtube_url" == str(col).lower() or
                    "lyrics" == str(col).lower() or
                    "youtube_url.1" == str(col).lower() or
                    "lyrics.1" == str(col).lower() or
                    "dancers" == str(col).lower()]
    df = df.drop(columns=cols_to_drop, errors="ignore")

    df = df.dropna(subset=['lyrics_english'])

    print("adding features...")
    # ------------ add one_mark regarding english
    df['is_english_main_lang'] = df['main_language'].astype(str).str.contains("english", case=False, na=False).astype(
        int)

    # -------------  add columns that summarize previous years

    df = df.sort_values(['country', 'year']).reset_index(drop=True)

    # 1. Total wins until this year
    # We'll create a cumulative count of wins (place==1) per country
    df['total_wins'] = (
        df.groupby('country')['place']
        .transform(lambda x: (x.shift() == 1).cumsum())
    )
    # 2. Did the country win last year
    df['won_last_year'] = df.groupby('country')['place'].shift(1) == 1

    # 3. Did the country come top 5 last year
    df['top5_last_year'] = df.groupby('country')['place'].shift(1).le(5)

    # Optional: convert boolean columns to int (0/1)
    df['won_last_year'] = df['won_last_year'].astype(int)
    df['top5_last_year'] = df['top5_last_year'].astype(int)

    # Fill missing sexuality with "straight"
    df['artist sexuality'] = df['artist sexuality'].fillna('straight')

    # ----------- add column about meaning of the song:

    results = df['lyrics_english'].apply(asm.analyze_song_theme)

    # Expand the dict into a DataFrame with the right keys
    results_df = pd.DataFrame(results.tolist(), index=df.index)

    # # Add the new columns to the original dataframe
    df['theme'] = results_df['theme']
    df['emotion'] = results_df['emotion']

    #re order table:
    priority_cols = [
        "year","host", "country", "artist", "song", "all_languages", "main_language","is_english_main_lang",
        "lyrics_original", "lyrics_english", "stage_director", "composers", "lyricists",
        "place", "points", "running_order", "total_wins", "won_last_year", "top5_last_year",
        "artist sexuality", "bpm", "tone", "theme","emotion", "top_3_words", "points_jury_final",
        "points_tele_final", "place_sf", "points_sf", "place_contest",
        "points_jury_sf", "points_tele_sf", "running_sf", "sf_num"
    ]

    # Add the rest of the columns automatically
    other_cols = [c for c in df.columns if c not in priority_cols]

    # Reorder DataFrame
    df = df[priority_cols + other_cols]

    # Step 8: Save cleaned dataset
    df.to_csv("final_merged.csv", index=False)
    print("✅ Cleaned dataset saved as final_merged.csv")


if __name__ == '__main__':
    create_dataset()
