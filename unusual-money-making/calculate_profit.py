import json
import requests
import webbrowser
from typing import Optional, Tuple

# API configuration (adjust as needed)
PRICE_API_URL = "https://prices.runescape.wiki/api/v1/osrs/latest"
PRICE_API_USER_AGENT = "unusual-money-makers"
PRICE_API_TIMEOUT = 10
MONEY_MAKER_JSON_PATH = "data/money_makers.json"
ITEM_MAPPING_JSON_PATH = "data/item_mapping.json"
GE_PRICES_URL = "https://prices.runescape.wiki/osrs/item"


def get_item_prices(item_id: int) -> Tuple[Optional[int], Optional[int], Optional[float]]:
    """
    Returns (high_price, low_price, avg_price) for an OSRS item.
    """
    if not item_id:
        return None, None, None

    response = requests.get(
        PRICE_API_URL,
        params={"id": item_id},
        headers={"User-Agent": PRICE_API_USER_AGENT},
        timeout=PRICE_API_TIMEOUT,
    )
    response.raise_for_status()

    item_prices = response.json()["data"][str(item_id)]

    high_price = item_prices.get("high")
    low_price = item_prices.get("low")

    if high_price is not None and low_price is not None:
        avg_price = (high_price + low_price) / 2
    else:
        avg_price = None

    return high_price, low_price, avg_price


def load_json_file(filepath: str) -> dict:
    """Load and return JSON file contents."""
    with open(filepath, "r") as f:
        return json.load(f)


def main():
    # Load data files
    money_makers = load_json_file(MONEY_MAKER_JSON_PATH)
    item_mapping = load_json_file(ITEM_MAPPING_JSON_PATH)

    # Create a dictionary for quick item lookup by name
    item_lookup = {item["name"]: item for item in item_mapping}

    results = []

    for recipe in money_makers:
        product_name = recipe["name"]
        quantity_produced = recipe["quantity_produced"]
        materials = recipe["materials"]
        skill = recipe["skill"]
        xp_per_action = recipe["xp_per_action"]
        actions_per_hour = recipe["actions_per_hour"]

        # Get product item ID and price
        if product_name not in item_lookup:
            print(f"Warning: Product '{product_name}' not found in item mapping, skipping.")
            continue

        product_item = item_lookup[product_name]
        product_id = product_item["id"]

        try:
            product_high, _, _ = get_item_prices(product_id)
        except Exception as e:
            print(f"Warning: Failed to get price for '{product_name}': {e}")
            continue

        if product_high is None:
            print(f"Warning: No price data for '{product_name}', skipping.")
            continue

        # Calculate material costs
        material_cost_per_action = 0
        material_details = []

        for material in materials:
            material_name = material["name"]
            material_quantity = material["quantity"]

            if material_name not in item_lookup:
                print(f"Warning: Material '{material_name}' not found in item mapping, skipping recipe.")
                break

            material_item = item_lookup[material_name]
            material_id = material_item["id"]

            try:
                _, material_low, _ = get_item_prices(material_id)
            except Exception as e:
                print(f"Warning: Failed to get price for material '{material_name}': {e}")
                break

            if material_low is None:
                print(f"Warning: No price data for material '{material_name}', skipping recipe.")
                break

            material_cost = material_low * material_quantity
            material_cost_per_action += material_cost
            material_details.append({
                "name": material_name,
                "quantity": material_quantity,
                "low_price": material_low,
                "item_id": material_id
            })
        else:
            # All materials were found and priced successfully
            # Calculate profit per action (with 2% tax)
            product_revenue = product_high * quantity_produced * 0.98
            profit_per_action = product_revenue - material_cost_per_action

            # Calculate profit per hour and XP per hour
            profit_per_hour = profit_per_action * actions_per_hour
            xp_per_hour = xp_per_action * actions_per_hour

            results.append({
                "product_name": product_name,
                "product_id": product_id,
                "product_high_price": product_high,
                "profit_per_action": profit_per_action,
                "profit_per_hour": profit_per_hour,
                "xp_per_hour": xp_per_hour,
                "skill": skill,
                "material_details": material_details
            })

    # Sort by profit per hour (descending)
    results.sort(key=lambda x: x["profit_per_hour"])

    # Print summary
    print("\n" + "=" * 120)
    print("OSRS PROFIT CALCULATOR SUMMARY")
    print("=" * 120)

    for idx, result in enumerate(results, 1):
        print(f"\n{idx}. {result['product_name']} ({result['skill']})")
        print(f"   Profit/Hour: {result['profit_per_hour']:,.0f} gp/hr")
        print(f"   XP/Hour: {result['xp_per_hour']:,.0f} xp/hr")
        print(f"   Product High Price (before tax): {result['product_high_price']:,} gp")
        print("   Materials:")
        for material in result["material_details"]:
            print(f"      - {material['name']}: {material['quantity']} x {material['low_price']:,} gp = {material['quantity'] * material['low_price']:,} gp")

    print("\n" + "=" * 120)

    # Prompt user for opening wiki pages
    print(f"\nTotal money makers: {len(results)}")
    try:
        user_input = input("How many would you like to open in your browser?")
        num_to_open = int(user_input)
        
        if num_to_open <= 0:
            print("Exiting.")
            return
        
        # Get the top N most profitable (from the end of results, since they're sorted ascending)
        num_to_open = min(num_to_open, len(results))
        most_profitable = results[-num_to_open:]
        most_profitable.reverse()

        print(f"\nOpening wiki pages for top {num_to_open} money maker(s)...")
        for result in most_profitable:
            # Open material pages
            for material in result["material_details"]:
                material_url = f"https://prices.runescape.wiki/osrs/item/{material['item_id']}"
                webbrowser.open(material_url)

            # Open product page
            product_url = f"{GE_PRICES_URL}/{result['product_id']}"
            webbrowser.open(product_url)
        
        print("Done!")
        
    except ValueError:
        print("Invalid input. Exiting script.")
        return
    except KeyboardInterrupt:
        print("\n\nExiting.")
        return


if __name__ == "__main__":
    main()
