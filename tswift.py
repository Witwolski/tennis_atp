from seleniumwire import webdriver
import logging
import time
from selenium.webdriver.remote.remote_connection import LOGGER
import warnings
from playsound import playsound
from pydub import AudioSegment
from pydub.playback import play
import os
from playsound import playsound


warnings.filterwarnings("ignore", category=DeprecationWarning)

# Disable all logging messages
logging.basicConfig(level=logging.CRITICAL)
LOGGER.setLevel(logging.CRITICAL)

# Specify the URL you want to scrape
url = "https://deals.ticketek.com.au/purchase/searchlist?keyword=Taylor%20Swift"

# Infinite loop to repeatedly check for tickets
while True:
    sound_file_path = r"C:\temp\mixkit-bell-notification-933.wav"
    # Create a Chrome webdriver in headless mode
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--log-level=3")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options=options)

    try:
        # Open the URL in Chrome
        x = driver.get(url)

        # Wait for some time to allow the page to load (you can adjust this based on your needs)
        y = driver.implicitly_wait(10)

        # Get the HTML content of the page
        html_content = driver.page_source

        # Check if "ticket left" or "tickets left" is in the HTML content
        if (
            "2 tickets left" not in html_content.lower()
            and "ticket left" not in html_content.lower()
            and "tickets left" in html_content.lower()
        ):
            print("Tickets are left!")
            playsound(sound_file_path)
        else:
            print("No tickets left.")

    finally:
        # Close the browser
        driver.quit()

    # Introduce a delay before the next iteration (you can adjust this based on your needs)
    delay_seconds = 5  # e.g., wait for 1 minute before checking again
    time.sleep(delay_seconds)
