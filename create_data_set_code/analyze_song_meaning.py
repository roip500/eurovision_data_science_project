from transformers import pipeline


def analyze_song_theme(lyrics: str) -> dict:
    """
    Analyze the main theme and emotion of a song based on its lyrics.
    Returns a dictionary with detected theme and emotion.
    """
    print(">> started new analyation")
    lyrics_clean = lyrics.replace("\n", " ")

    # --- 1. Expanded Theme Detection using Zero-Shot Classification ---
    themes = [
        "love", "friendship", "life", "relationships", "self-discovery",
        "happiness", "sadness", "heartbreak", "party", "hope", "freedom",
        "identity", "loneliness", "betrayal", "forgiveness", "dreams",
        "adventure", "family", "nature", "success", "regret", "courage",
        "inspiration", "nostalgia", "passion", "fun", "overcoming obstacles",
        "faith", "revenge", "war", "peace", "change", "youth", "aging",
        "mental health", "friendship loss", "jealousy", "addiction"
    ]

    classifier = pipeline("zero-shot-classification",
                          model="facebook/bart-large-mnli")

    theme_result = classifier(lyrics_clean, candidate_labels=themes)
    top_theme = theme_result['labels'][0]

    # --- 2. Emotion Analysis (detailed emotions) using top_k=1 instead of deprecated return_all_scores ---
    emotion_analyzer = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=1  # replaces return_all_scores=False
    )
    emotion = emotion_analyzer(lyrics_clean[:512])  # first 512 chars

    return {
        "theme": top_theme,
        "emotion": emotion[0]
    }


# Example usage
if __name__ == "__main__":
    lyrics = """
    Is this the real life? Is this just fantasy?
    Caught in a landslide, no escape from reality...
    """
    result = analyze_song_theme(lyrics)
    print("=== Theme of the song ===")
    print(result["theme"])
    print("\n=== Emotion of the song ===")
    print(result["emotion"])
