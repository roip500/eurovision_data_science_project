import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict
from matplotlib.patches import Patch

sns.set(style="whitegrid")

def load_eurovision_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_winner_languages(data):
    rows = []
    for contest in data:
        year = contest.get("year")
        final_round = next((r for r in contest.get("rounds", []) if r["name"] == "final"), None)
        if not final_round:
            continue
        winning_perf = next((p for p in final_round.get("performances", []) if p["place"] == 1), None)
        if not winning_perf:
            continue
        winner_id = winning_perf["contestantId"]
        contestant = next((c for c in contest.get("contestants", []) if c["id"] == winner_id), None)
        if not contestant:
            continue
        lyrics = contestant.get("lyrics", [])
        if lyrics:
            languages = lyrics[0].get("languages", ["Unknown"])
            lang = " & ".join(languages)
        else:
            lang = "Unknown"
        rows.append({"year": year, "language": lang})
    return pd.DataFrame(rows)

def plot_cumulative_language_wins(df, top_n=5):
    df = df.copy()
    df['language'] = df['language'].replace({
        'English version': 'English',
        'english': 'English',
        'eng': 'English'
    })

    counts = df['language'].value_counts()
    top_languages = counts.head(top_n).index.tolist()

    df_top = df[df['language'].isin(top_languages)].copy()
    df_top['count'] = 1

    cum_df = (
        df_top.pivot_table(index='year', columns='language', values='count', aggfunc='sum')
        .fillna(0)
        .cumsum()
        .sort_index()
    )

    plt.figure(figsize=(12, 6))
    for lang in cum_df.columns:
        plt.plot(cum_df.index, cum_df[lang], label=lang, linewidth=2)

    plt.title(f"Cumulative Wins for Top {top_n} Languages", fontsize=14)
    plt.xlabel("Year")
    plt.ylabel("Total Wins")
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.legend(title="Language", fontsize=10)
    plt.tight_layout()
    plt.show()

def plot_language_win_heatmap(winners_df):
    df = winners_df.copy()
    df["language"] = df["language"].replace({"English version": "English"})

    heatmap_df = (
        df.groupby(["year", "language"])
        .size()
        .reset_index(name="wins")
        .pivot(index="year", columns="language", values="wins")
        .fillna(0)
        .astype(int)
    )

    if 2020 not in heatmap_df.index:
        empty_row = pd.DataFrame(
            [[-1] * heatmap_df.shape[1]],
            columns=heatmap_df.columns,
            index=[2020]
        )
        heatmap_df = pd.concat([heatmap_df, empty_row])
        heatmap_df = heatmap_df.sort_index()

    total_wins = heatmap_df.replace(-1, 0).sum()
    filtered_langs = total_wins[total_wins >= 2].index
    heatmap_df = heatmap_df[filtered_langs]
    heatmap_df = heatmap_df[heatmap_df.sum().sort_values(ascending=False).index]

    cmap = sns.color_palette(["#d1d5db", "#f2f2f2", "#1f77b4"])
    bounds = [-1.5, -0.5, 0.5, 1.5]
    norm = plt.Normalize(vmin=-1.5, vmax=1.5)

    plt.figure(figsize=(12, 8))
    sns.heatmap(
        heatmap_df.T,
        cmap=cmap,
        linewidths=0.5,
        linecolor='gray',
        cbar=False,
        norm=norm,
        annot=False
    )

    legend_elements = [
        Patch(facecolor="#1f77b4", edgecolor='gray', label='Win'),
        Patch(facecolor="#f2f2f2", edgecolor='gray', label='No Win'),
        Patch(facecolor="#d1d5db", edgecolor='gray', label='No Contest (COVID)'),
    ]
    plt.legend(
        handles=legend_elements,
        title="Legend",
        loc="upper left",
        bbox_to_anchor=(1.01, 1)
    )

    plt.title("Eurovision Winning Languages by Year (1956–2024)", fontsize=14)
    plt.xlabel("Year")
    plt.ylabel("Language")
    plt.tight_layout()
    plt.show()

def plot_participation_trends(data):
    """
    Plot the number of participating countries per year to support the historical claim
    about post-1991 expansion and diversity.
    """
    participation = []

    for contest in data:
        year = contest.get("year")
        contestants = contest.get("contestants", [])
        country_count = len(set(c.get("country") for c in contestants if c.get("country")))
        participation.append({"year": year, "countries": country_count})

    df = pd.DataFrame(participation).sort_values("year")

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="year", y="countries", marker="o", linewidth=2)

    # Highlight the post-Cold War turning point
    plt.axvline(x=1991, color="gray", linestyle="--", label="1991 (Post-Cold War Era)")

    plt.title("Eurovision Participation Over Time", fontsize=14)
    plt.xlabel("Year")
    plt.ylabel("Number of Participating Countries")
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    data_path = Path("../basic_datasets/eurovision.json")
    euro_data = load_eurovision_data(data_path)
    winners_df = extract_winner_languages(euro_data)

    # Plot 1: Participation trend (your new analysis)
    plot_participation_trends(euro_data)

    # Plot 2: Heatmap of winner languages
    plot_language_win_heatmap(winners_df)

    # Optional: cumulative wins (can uncomment if needed)
    # plot_cumulative_language_wins(winners_df)

if __name__ == "__main__":
    main()
