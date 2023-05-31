from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from tqdm import tqdm

options = Options()
options.add_argument("--headless")

browser = webdriver.Chrome(
    r"C:\Users\chris\OneDrive\Documents\GitHub\tennis_atp\chromedriver.exe",
    options=options,
)

browser.get(
    "https://www.atptour.com/en/rankings/singles?rankRange=1-5000&rankDate=2022-07-18"
)
