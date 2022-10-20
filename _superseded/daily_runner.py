from Elo_AllMatches_six_months_day_by_day_all_Today import all
from Elo_AllMatches_six_months_day_by_day_Clay_Today import clay
from Elo_AllMatches_six_months_day_by_day_Hard_Today import hard

from tennisexplorer_Odds_Today import Today
import pandas as pd
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
import sys

Today()

fav_df, dog_df = all()
fav_df2, dog_df2 = clay()
fav_df3, dog_df3 = hard()

combined_fav = pd.concat([fav_df, fav_df2, fav_df3])
combined_dog = pd.concat([dog_df, dog_df2, dog_df3])
time_now = datetime.datetime.now() + datetime.timedelta(minutes=0)
time_10 = datetime.datetime.now() + datetime.timedelta(minutes=20)
time_10_formatted = time_10.strftime("%H:%M")
time_now_formatted = time_now.strftime("%H:%M")
time_now_formatted_2 = time_now.strftime("%Y_%m_%d")

time_10_before = datetime.datetime.now() + datetime.timedelta(minutes=-20)
time_10_before_formatted = time_10_before.strftime("%H:%M")

smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo()
smtpserver.login("christophermarcwitt@gmail.com", "gpjatpbqyambtxmi")
sent_from = "christophermarcwitt@gmail.com"
sent_to = ["christophermarcwitt@gmail.com"]


combined_fav.rename(
    columns={"Elo_Fav": "Selection", "Elo_Fav_Odds": "Odds", "Elo_Dog": "Opposition"},
    inplace=True,
)
combined_dog.rename(
    columns={"Elo_Dog": "Selection", "Elo_Dog_Odds": "Odds", "Elo_Fav": "Opposition"},
    inplace=True,
)

combined_selection = pd.concat([combined_fav, combined_dog])
combined_selection["Result"] = combined_selection.apply(
    lambda x: "Win" if x["Selection"] == x["Winner"] else "Loss", axis=1
)
combined_selection = combined_selection[
    ["Selection", "Odds", "Opposition", "Resulted", "Time", "Result"]
]

if combined_selection.empty == False:
    selection = (
        combined_selection[
            (combined_selection["Resulted"] == "False")
            & (combined_selection["Time"] < time_10_formatted)
            & (combined_selection["Time"] > time_10_before_formatted)
        ]
        .drop_duplicates()
        .sort_values(by="Time")
        # .to_string(index=False, header=False)
    )
    selection.drop(columns="Result", inplace=True)

    if selection.empty == False:
        recipients = ["christophermarcwitt@gmail.com"]
        emaillist = [elem.strip().split(",") for elem in recipients]
        msg = MIMEMultipart()
        msg["Subject"] = "Your Subject"
        msg["From"] = "christophermarcwitt@gmail.com"

        html = """\
            <html>
            <head></head>
            <body>
                {0}
            </body>
            </html>
            """.format(
            selection.to_html(index=False)
        )

        part1 = MIMEText(html, "html")
        msg.attach(part1)

        smtpserver.sendmail(msg["From"], emaillist, msg.as_string())

combined_selection.drop_duplicates().sort_values(by="Time").to_csv(
    r"C:\Git\tennis_atp\daily_{}.csv".format(time_now_formatted_2), index=False
)
