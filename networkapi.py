from playwright.sync_api import sync_playwright


def test_json(response):
    try:
        print(response.json())
    except:
        pass


def run(playwright):
    chromium = playwright.chromium
    browser = chromium.launch()
    page = browser.new_page()
    # Subscribe to "request" and "response" events.
    # page.on("request", lambda request: print(">>", request.method, request.url))
    page.on("response", lambda response: test_json(response))
    page.goto("https://www.tennisexplorer.com/matches/")
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
