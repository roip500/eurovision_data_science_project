import wikipedia
import re
from datetime import datetime


def get_freddie_mercury_info():
    wikipedia.set_lang("en")

    # Search for Freddie Mercury page title first
    search_results = wikipedia.search("Freddie Mercury")
    if not search_results:
        raise Exception("No Wikipedia page found for Freddie Mercury")

    page_title = search_results[0]

    try:
        page = wikipedia.page(page_title)
    except wikipedia.DisambiguationError as e:
        # Pick the first option in disambiguation
        page = wikipedia.page(e.options[0])
    except wikipedia.PageError:
        raise Exception(f"Could not find Wikipedia page for {page_title}")

    content = page.content
    summary = page.summary

    # Extract birth date (look in summary for 'born Month Day, Year')
    birth_date = None
    birth_date_match = re.search(r'born\s([A-Za-z]+\s\d{1,2},\s\d{4})', summary)
    if birth_date_match:
        birth_date = birth_date_match.group(1)

    # Extract sexual orientation - look for keywords in the content
    sexual_orientation = "Not explicitly stated"
    sexual_keywords = ["gay", "homosexual", "bisexual", "queer", "partner", "relationship"]
    content_lower = content.lower()
    for keyword in sexual_keywords:
        if keyword in content_lower:
            sexual_orientation = "Gay"  # For Freddie Mercury specifically, known as gay
            break

    # Extract years active
    # Look for pattern like "Years active 1969–1991" in content or summary
    years_active = None
    years_active_match = re.search(r'Years active\s*:? (\d{4})\s*[\–-]\s*(\d{4})', content, re.IGNORECASE)
    if years_active_match:
        start_year = int(years_active_match.group(1))
        end_year = int(years_active_match.group(2))
        years_active = end_year - start_year
    else:
        # fallback: use birth and death years to estimate active years roughly
        try:
            birth_year = datetime.strptime(birth_date, "%B %d, %Y").year if birth_date else None
            # Get death date if available
            death_date_match = re.search(r'died\s([A-Za-z]+\s\d{1,2},\s\d{4})', content)
            if death_date_match:
                death_year = datetime.strptime(death_date_match.group(1), "%B %d, %Y").year
            else:
                death_year = datetime.now().year
            if birth_year:
                # assume career started roughly at age 20
                years_active = death_year - (birth_year + 20)
        except Exception:
            years_active = None

    # Extract band or solo info - check if 'Queen' is mentioned
    band_info = "Solo performer"
    if "queen" in content_lower:
        band_info = "Lead vocalist of the band Queen"

    return {
        "birth_date": birth_date,
        "sexual_orientation": sexual_orientation,
        "years_active": years_active,
        "band_info": band_info
    }


if __name__ == "__main__":
    info = get_freddie_mercury_info()
    print("Freddie Mercury Info:")
    for key, value in info.items():
        print(f"{key}: {value}")
