# OSRS Leagues Reward Value
Realtime Old School RuneScape leagues rewards gp per point calculator.

The [OSRS leagues wiki](https://oldschool.runescape.wiki/w/Leagues_Reward_Shop) page has a "GP per point" calculation, but prices for these items flucuate often, making wiki GE prices outdated.

Uses the latest GE prices from the [wiki real time prices API](https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices).

## How to Run

Run `python calculate_value.py`

Output csv will appear in the output folder.

## When new leagues rewards come out

[item_mapping.json](data/item_mapping.json) contains information on all items in OSRS (from the wiki real time prices API). If new items are released, run `python update_mapping.py` or copy them from [here](https://prices.runescape.wiki/api/v1/osrs/mapping).

[leagues-rewards.csv](data/leagues-rewards.csv) contains information on the leagues rewards (item name, point cost, quantity sold). When new leagues rewards are released, add new rows using the [reward shop page](https://oldschool.runescape.wiki/w/Leagues_Reward_Shop) as reference. But make sure the item name matches the name in [item_mapping.json](data/item_mapping.json).