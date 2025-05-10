from tennisexplorer_Odds_Today import Today


from analysis_daily import analysis

from predictions import Predictions
from Elo_AllMatches_six_months import Elo

import logging
import os
import datetime


today = datetime.datetime.now()
file_path = "error.log"

try:
    os.remove(file_path)
    # print(f"File '{file_path}' deleted successfully.")
except OSError as e:
    print(f"Error: {file_path} - {e.strerror}.")


logging.basicConfig(filename="error.log", level=logging.ERROR)

try:
    Elo("Hard")
    Elo("Clay")
    Elo("Grass")
    Today()
    analysis()
    # Predictions("Hard", today)
    # Predictions("Clay", today)
    # Predictions("Grass", today)

    # Elo("Grass")
    # Elo("%")
    pass
except Exception as e:
    logging.error("An error occurred: %s", str(e))

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd


def send_email(subject, body, attachment=False):
    sender_email = "christophermarcwitt@gmail.com"
    receiver_email = "christophermarcwitt@gmail.com"
    password = "fknl oseb qtrv hklu"

    message = MIMEMultipart()
    message.attach(MIMEText(body, "plain"))
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email
    # Read CSV files into pandas DataFrames
    clay_df = pd.read_csv("Fav_Clay.csv")
    hard_df = pd.read_csv("Fav_Hard.csv")
    grass_df = pd.read_csv("Fav_Grass.csv")

    # Combine DataFrames
    combined_df = pd.concat([clay_df, hard_df, grass_df]).sort_values(
        by="Time", ascending=True
    )

    # Write combined DataFrame to a new CSV file
    combined_df.to_csv("Combined_Favorites.csv", index=False)

    # Read CSV files into pandas DataFrames
    clay_df = pd.read_csv("Dog_Clay.csv")
    hard_df = pd.read_csv("Dog_Hard.csv")
    grass_df = pd.read_csv("Dog_Grass.csv")

    # Combine DataFrames
    combined_df = pd.concat([clay_df, hard_df, grass_df]).sort_values(
        by="Time", ascending=True
    )

    # Write combined DataFrame to a new CSV file
    combined_df.to_csv("Combined_Dogs.csv", index=False)

    if attachment:
        # List of attachment file paths
        file_paths = ["Combined_Favorites.csv", "Combined_Dogs.csv"]

        # Loop through each file path and attach to the email
        for file_path in file_paths:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {file_path}",
            )
            message.attach(part)
    text = message.as_string()
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, text)
    server.quit()


with open("error.log", "r") as f:
    error_log = f.read()

if "ERROR" in error_log:
    print(error_log)
    # send_email("Error in Todays Data", error_log, False)
# else:
#    send_email("Todays Predictions", "See Attached", True)
