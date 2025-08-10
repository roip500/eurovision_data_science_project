import os
from selenium import webdriver
from selenium.webdriver.safari.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_score(year):
    url = "https://eurovisionworld.com/eurovision/" + year

    options = Options()
    options.headless = True

    driver = webdriver.Safari(options=options)
    driver.get(url)

    time.sleep(3)  # wait for JS

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    table = soup.find("table", class_="scoreboard_table")
    if not table:
        raise ValueError("Could not find the scoreboard_table.")

    df = pd.read_html(str(table))[0]

    # Drop unwanted columns
    df = df.drop(df.columns[[0, 1, -1]], axis=1)
    df.rename(columns={df.columns[0]: "Country"}, inplace=True)
    df.rename(columns={df.columns[1]: "total_judge_points"}, inplace=True)

    # Country code to full name mapping (add more as needed)
    country_map = {
        "al": "Albania",
        "at": "Austria",
        "am": "Armenia",
        "az": "Azerbaijan",
        "by": "Belarus",
        "be": "Belgium",
        "ba": "Bosnia & Herzegovina",
        "bg": "Bulgaria",
        "hr": "Croatia",
        "cy": "Cyprus",
        "cz": "Czech Republic",
        "dk": "Denmark",
        "ee": "Estonia",
        "fi": "Finland",
        "fr": "France",
        "ge": "Georgia",
        "de": "Germany",
        "gr": "Greece",
        "hu": "Hungary",
        "is": "Iceland",
        "ie": "Ireland",
        "il": "Israel",
        "it": "Italy",
        "lv": "Latvia",
        "lt": "Lithuania",
        "lu": "Luxembourg",
        "mt": "Malta",
        "md": "Moldova",
        "me": "Montenegro",
        "nl": "Netherlands",
        "no": "Norway",
        "pl": "Poland",
        "pt": "Portugal",
        "ro": "Romania",
        "ru": "Russia",
        "rs": "Serbia",
        "sk": "Slovakia",
        "si": "Slovenia",
        "es": "Spain",
        "se": "Sweden",
        "ch": "Switzerland",
        "ua": "Ukraine",
        "gb": "United Kingdom",
        # Add any missing codes if needed
    }

    # Extract header <td> elements with voting countries (skip first 4 columns and last empty one)
    header_tds = table.find("thead").find("tr").find_all("td")[1:-1]

    country_codes = [td.get("data-from") for td in header_tds]
    columns = [country_map.get(code, code) for code in country_codes if country_codes]

    for i in range(len(columns)):
        df.rename(columns={df.columns[i+2]: columns[i]+" Jury"}, inplace=True)

    df.fillna(0, inplace=True)

    return df


def main():
    # Path to your local dataset folder
    dataset_folder = "basic_datasets"

    # Local file paths
    contestants_file = os.path.join(dataset_folder, "contestants.csv")
    votes_file = os.path.join(dataset_folder, "votes.csv")
    audio_features_file = os.path.join(dataset_folder, "audio_features.csv")

    print("📥 Loading datasets from local folder...")
    contestants = pd.read_csv(contestants_file)
    votes = pd.read_csv(votes_file)

    # Create mapping from country ID to country name
    id_to_country = contestants.set_index("to_country_id")["to_country"].to_dict()

    # Map voter country IDs to country names in votes DataFrame
    votes["from_country_name"] = votes["from_country_id"].map(id_to_country)

    # Filter votes for final round only
    votes_final = votes[votes["round"].str.lower() == "final"]

    # Separate jury and televote votes, using mapped names for pivot
    votes_jury = votes_final[votes_final["jury_points"].notna()]
    votes_jury = votes_jury[["year", "to_country_id", "from_country_name", "jury_points"]].copy()
    votes_jury.rename(columns={"jury_points": "points", "from_country_name": "from_country"}, inplace=True)

    votes_tv = votes_final[votes_final["tele_points"].notna()]
    votes_tv = votes_tv[["year", "to_country_id", "from_country_name", "tele_points"]].copy()
    votes_tv.rename(columns={"tele_points": "points", "from_country_name": "from_country"}, inplace=True)

    # Pivot votes into wide format with voter country names as columns
    def pivot_votes(df, suffix):
        p = df.pivot_table(
            index=["year", "to_country_id"],
            columns="from_country",
            values="points",
            fill_value=0
        ).reset_index()
        return p.rename(columns={col: f"{col} {suffix}" for col in p.columns if col not in ["year", "to_country_id"]})

    votes_jury_pivot = pivot_votes(votes_jury, "Jury")
    votes_tv_pivot = pivot_votes(votes_tv, "Televote")

    # Merge jury and televote votes
    votes_combined = pd.merge(
        votes_jury_pivot,
        votes_tv_pivot,
        on=["year", "to_country_id"],
        how="outer"
    ).fillna(0)

    # Filter contestants for entries with a final placement
    final_songs = contestants[contestants["place_final"].notna()]

    # Merge contestants with votes on year and country id
    df = pd.merge(
        final_songs,
        votes_combined,
        left_on=["year", "to_country_id"],
        right_on=["year", "to_country_id"],
        how="left"
    )

    # Drop the 'to_country_id' column so the table shows country names only
    df = df.drop(columns=["to_country_id"])

    # Add audio features if available locally
    if os.path.exists(audio_features_file):
        print("🎵 Adding audio features from local file...")
        audio_df = pd.read_csv(audio_features_file)
        df = pd.merge(
            df,
            audio_df[["year", "country", "tempo", "danceability", "energy", "loudness", "spectral_centroid"]],
            left_on=["year", "to_country"],
            right_on=["year", "country"],
            how="left"
        )
    else:
        print("⚠️ audio_features.csv not found locally — skipping audio features.")

    # Define main columns to keep and rename for clarity
    main_cols = [
        "year",
        "to_country",  # country
        "performer",  # artist
        "song",
        "language" if "language" in df.columns else None,
        "host_city" if "host_city" in df.columns else None,
        "running_final",
        "place_final",
        "points_final",
        "points_jury_final",
        "points_tele_final",
        "place_sf",
        "points_sf",
        "youtube_url"
    ]
    main_cols = [c for c in main_cols if c is not None]

    # Audio feature columns if present
    audio_cols = []
    if "tempo" in df.columns:
        audio_cols = ["tempo", "danceability", "energy", "loudness", "spectral_centroid"]

    # Voting columns: all except main, audio, and helper columns
    excluded_cols = set(main_cols + ["year", "country"] + audio_cols)
    vote_cols = sorted(
        [col for col in df.columns if col not in excluded_cols],
        key=lambda x: x.replace(" Jury", "").replace(" Televote", "")
    )

    # Final column order: song info, audio features, vote columns, then youtube_url
    columns_to_keep = main_cols + audio_cols + vote_cols + ["lyrics", "youtube_url"]

    df_final = df[columns_to_keep]

    # # Save to CSV instead of Excel
    # output_file = "datasets/eurovision_dataset_1.csv"
    # df_final.to_csv(output_file, index=False)

    print("🕐 Adding jury scores per year from 1957 to 2016...")

    # We'll copy df_final to avoid modifying original while merging
    df_with_jury_scores = df_final.copy()

    for year in range(1957, 2015 + 1):
        print(f"Processing year {year}...")
        try:
            year_df = get_score(str(year))

            mask_year = df_with_jury_scores["year"] == int(year)  # year as int in df

            for idx, row in year_df.iterrows():
                country = row["Country"]
                total_points = row["total_judge_points"]

                mask = mask_year & (df_with_jury_scores["to_country"] == country)

                df_with_jury_scores.loc[mask, "points_jury_final"] = total_points
                df_with_jury_scores.loc[mask, "points_final"] = total_points

                for voter_country in year_df.columns[2:]:
                    if voter_country in df_with_jury_scores.columns:
                        df_with_jury_scores.loc[mask, voter_country] = row[voter_country]

        except Exception as e:
            print(f"Skipping year {year} due to error: {e}")

    # Save the augmented dataframe
    output_augmented = "datasets/eurovision_dataset_1.csv"
    df_with_jury_scores.to_csv(output_augmented, index=False)
    print(f"✅ Augmented dataset with jury scores saved to {output_augmented}")

if __name__ == "__main__":
    main()