from Elo_AllMatches_six_months_day_by_day_all_Today import all
from Elo_AllMatches_six_months_day_by_day_Clay_Today import clay
from Elo_AllMatches_six_months_day_by_day_Hard_Today import hard
from tennisexplorer_Odds_Today import Today
import pandas as pd


Today()

fav_df, dog_df = all()
fav_df2, dog_df2 = clay()
fav_df3, dog_df3 = hard()

combined_fav = pd.concat([fav_df, fav_df2, fav_df3])
combined_dog = pd.concat([dog_df, dog_df2, dog_df3])

if combined_fav.empty == False:
    print(
        combined_fav[["Elo_Fav", "Elo_Fav_Odds", "Elo_Dog", "Resulted", "Time"]][
            combined_fav["Resulted"] == "False"
        ]
        .drop_duplicates()
        .sort_values(by="Time")
    )
if combined_dog.empty == False:
    print(
        combined_dog[["Elo_Dog", "Elo_Dog_Odds", "Elo_Fav", "Resulted", "Time"]][
            combined_dog["Resulted"] == "False"
        ]
        .drop_duplicates()
        .sort_values(by="Time")
    )
