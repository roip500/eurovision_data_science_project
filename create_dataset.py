from create_data_set_code import extract_song_db_2, extract_song_db_1, lgtbq_artist_list, merge_datasets
import pandas as pd

def create_dataset():
    # extract_song_db_1.main()  # mute this command if dataset1 exists - takes long
    extract_song_db_2.main()
    lgtbq_artist_list.main()
    merge_datasets.merge_datasets()

    #things to edit out: all ros that the year arent between 1956 and 2025
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
                    "lyrics.1" == str(col).lower()]
    df = df.drop(columns=cols_to_drop, errors="ignore")

    # Step 7: sort by year
    df = df.sort_values(by="year", ascending=True)

    # Step 8: Save cleaned dataset
    df.to_csv("datasets/final_merged.csv", index=False)
    print("✅ Cleaned dataset saved as final_cleaned.csv")


if __name__ == '__main__':
    create_dataset()
