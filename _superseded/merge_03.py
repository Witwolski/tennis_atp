import pandas as pd

todays_matches = pd.read_excel("Bets_Today.xlsx")
todays_matches = todays_matches.round({"Thresh": 1})

prev_analysis = pd.read_excel("analysis.xlsx")
prev_analysis = prev_analysis[prev_analysis["FavDog"] == "Fav"]

combine_data = pd.merge(
    todays_matches,
    prev_analysis,
    how="inner",
    left_on=["Sex", "Thresh", "Higher"],
    right_on=["Sex", "Thresh", "HigherLower"],
    suffixes=["", "_y"],
)
combine_data["Filter"] = combine_data.apply(
    lambda x: True if x["WinsLosses_y"] <= x["WinsLosses"] else False, axis=1
)

filtered_data = combine_data[combine_data["Filter"] == True]
filtered_data.sort_values(by="WinsLosses_y", ascending=False, inplace=True)

output_data = filtered_data[
    [
        "Sex",
        "Elo_Fav",
        "Elo_Dog",
        "Elo_Fav_Odds",
        "Elo_Fav_Est_Odds",
        "WinsLosses",
        "WinsLosses_y",
        "WinPercent",
        "Games",
        "Profit",
        "Games_y",
        "Profit_y",
    ]
]
output_data.drop_duplicates(subset="Elo_Fav").to_excel(
    "DailyFiltered.xlsx", index=False
)
