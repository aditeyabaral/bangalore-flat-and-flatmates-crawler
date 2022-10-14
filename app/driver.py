import os
from selenium import webdriver


class Driver:
    def __init__(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--ignore-ssl-errors=yes")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--allow-running-insecure-content")
        if os.path.expanduser("~").startswith("/app"):
            self.chrome_options.binary_location = "/app/.apt/usr/bin/google-chrome"
            self.chrome = webdriver.Chrome(
                executable_path="/app/.chromedriver/bin/chromedriver",
                options=self.chrome_options,
            )
        else:
            if "./chromedriver" in os.listdir():
                chromedriver_path = "./chromedriver"
            elif "./chromedriver.exe" in os.listdir():
                chromedriver_path = "./chromedriver.exe"
            else:
                chromedriver_path = "chromedriver"

            self.chrome = webdriver.Chrome(
                executable_path=chromedriver_path, options=self.chrome_options
            )
        self.chrome.execute_cdp_cmd(
            "Emulation.setTimezoneOverride", {"timezoneId": "Asia/Kolkata"}
        )

    def get_driver(self):
        return self.chrome

    def open_facebook(self):
        self.chrome.get("https://www.facebook.com")
