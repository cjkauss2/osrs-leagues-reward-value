import os
import json
import requests
from pathlib import Path

MAPPING_API_URL = "https://prices.runescape.wiki/api/v1/osrs/mapping"
MAPPING_API_USER_AGENT = "leagues-rewards-value"
MAPPING_API_TIMEOUT = 30

OUTPUT_FILE = Path("data/item_mapping.json")


def main():
    response = requests.get(
        MAPPING_API_URL, 
        headers={"User-Agent": MAPPING_API_USER_AGENT},
        timeout=MAPPING_API_TIMEOUT
    )
    response.raise_for_status()

    data = response.json()

    # Overwrite the file if it already exists
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Saved item mapping to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()