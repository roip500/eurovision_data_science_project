import pandas as pd
import requests
from bs4 import BeautifulSoup

def main():
    url = "https://en.wikipedia.org/wiki/List_of_LGBTQ_participants_in_the_Eurovision_Song_Contest"

    # Fetch HTML
    html = requests.get(url, verify=False).text

    # Parse HTML
    soup = BeautifulSoup(html, "html.parser")

    # Get the second table
    tables_html = soup.find_all("table", {"class": "wikitable"})
    target_table = tables_html[1]

    # Load table into DataFrame
    df = pd.read_html(str(target_table))[0]

    # Extract artist links
    links = []
    placements = []  # store placement category based on color

    for row in target_table.find_all("tr")[1:]:  # skip header
        # --- Extract link ---
        cell = row.find("td")
        if cell and cell.find("a"):
            link = cell.find("a")["href"]
            if link.startswith("/wiki/"):
                link = "https://en.wikipedia.org" + link
            links.append(link)
        else:
            links.append(None)

        # --- Determine placement from style ---
        style = row.get("style", "").lower()
        tds = row.find_all("td")
        bgc = row.get("bgcolor", "").lower()
        if (not style or not bgc) and tds:
            # Sometimes color is on a <td> instead of the <tr>
            for td in tds:
                if "background" in td.get("style", "").lower():
                    style = td["style"].lower()
                    break

        if "gold" in bgc:
            placements.append("1st place")
        elif "silver" in style:
            placements.append("2nd place")
        elif "#cc9966" in style or "bronze" in style:
            placements.append("3rd place")
        else:
            placements.append("None")

    # Add columns
    df["Artist Link"] = links
    df["Placement"] = placements

    # Save to Excel
    df.to_excel("datasets/lgbtq_eurovision_artists.xlsx", index=False)

    print("✅ Excel file created with artist names, links, and placement category!")

if __name__ == "__main__":
    main()