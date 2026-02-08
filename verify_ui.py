from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:5173")
        page.wait_for_timeout(2000) # Wait for initial load
        page.screenshot(path="current_ui_start.png")

        # Click "НАЧАТЬ ТРЕНИРОВКУ"
        page.click("text=НАЧАТЬ ТРЕНИРОВКУ")
        page.wait_for_timeout(2000) # Wait for game to start
        page.screenshot(path="current_ui_game.png")

        browser.close()

if __name__ == "__main__":
    run()
