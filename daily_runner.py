from Elo_AllMatches_six_months_day_by_day_all_Today import all
from Elo_AllMatches_six_months_day_by_day_Clay_Today import clay
from Elo_AllMatches_six_months_day_by_day_Hard_Today import hard

from tennisexplorer_Odds_Today import Today
import pandas as pd
import smtplib
import datetime

Today()

fav_df, dog_df = all()
fav_df2, dog_df2 = clay()
fav_df3, dog_df3 = hard()

combined_fav = pd.concat([fav_df, fav_df2, fav_df3])
combined_dog = pd.concat([dog_df, dog_df2, dog_df3])
time_10 = datetime.datetime.now() + datetime.timedelta(minutes=20)
time_10_formatted = time_10.strftime("%H:%M")

smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo()
smtpserver.login("christophermarcwitt@gmail.com", "gpjatpbqyambtxmi")
sent_from = "christophermarcwitt@gmail.com"
sent_to = ["christophermarcwitt@gmail.com"]

if combined_fav.empty == False:
    fav = (
        combined_fav[["Elo_Fav", "Elo_Fav_Odds", "Time"]][
            (combined_fav["Resulted"] == "False")
            & (combined_fav["Time"] < time_10_formatted)
        ]
        .drop_duplicates()
        .sort_values(by="Time")
        .to_string(index=False, header=False)
    )
    sent_subject = "Fav 10 mins"
    sent_body = fav

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (
        sent_from,
        ", ".join(sent_to),
        sent_subject,
        sent_body,
    )
    smtpserver.sendmail(sent_from, sent_to, email_text)


if combined_dog.empty == False:

    dog = (
        combined_dog[["Elo_Dog", "Elo_Dog_Odds", "Time"]][
            (combined_dog["Resulted"] == "False")
            & (combined_dog["Time"] < time_10_formatted)
        ]
        .drop_duplicates()
        .sort_values(by="Time")
        .to_string(index=False, header=False)
    )

    sent_subject = "Dog < 10 mins"
    sent_body = dog

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (
        sent_from,
        ", ".join(sent_to),
        sent_subject,
        sent_body,
    )
    smtpserver.sendmail(sent_from, sent_to, email_text)


smtpserver.close
