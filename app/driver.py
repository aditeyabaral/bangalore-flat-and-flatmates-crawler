import os
import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Driver:
    def __init__(self):
        self.chrome_options = webdriver.ChromeOptions()
        # self.chrome_options.add_argument("--headless")
        # self.chrome_options.add_argument("--no-sandbox")
        # self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--ignore-ssl-errors=yes")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--allow-running-insecure-content")
        self.chrome_options.add_argument("--disable-web-security")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-geolocation")
        self.chrome_options.add_argument("--disable-notifications")
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

    def recurse_through_divs(self, div_element, text):
        divs = div_element.find_elements(By.XPATH, ".//div")
        if len(divs) == 0:
            return div_element.text
        for div in divs:
            text += self.recurse_through_divs(div, text)
        return text
    
    def recurse_through_divs_and_find_role(self, div_element):
        if div_element.role == "feed":
            return div_element
        divs = div_element.find_elements(By.XPATH, ".//div")
        if len(divs) == 0:
            return None
        for div in divs:
            role = self.recurse_through_divs_and_find_role(div)
            if role is not None:
                return role


    def open_facebook(self):
        self.chrome.get("https://www.facebook.com/login/")

    def login_facebook(self, username, password):
        if self.chrome.current_url != "https://www.facebook.com/login/":
            raise("Facebook is not open. Use open_facebook() to open Facebook first.")

        WebDriverWait(self.chrome, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"email\"]"))
        )
        email_input = self.chrome.find_element(By.XPATH, "//*[@id=\"email\"]")
        password_input = self.chrome.find_element(By.XPATH, "//*[@id=\"pass\"]")
        email_input.send_keys(username)
        password_input.send_keys(password)
        self.chrome.find_element(By.XPATH, "//button[@type='submit']").click()
    
    def visit_group(self, group_name):
        time.sleep(3)
        url = f"https://www.facebook.com/groups/{group_name}/buy_sell_discussion?sorting_setting=RECENT_ACTIVITY"
        self.chrome.get(url)

    def scrape_posts_on_page(self):
        time.sleep(4)
        for _ in range(5):
            ActionChains(self.chrome).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(0.5)

        # find all where div have dir=auto
        divs = self.chrome.find_elements(By.XPATH, "//span[@dir='auto']")
        for div in divs:
            print(div.text)

        # role_element = self.chrome.find_elements(By.XPATH, "//*[@role='feed']")[-1]
        # print(role_element)
        # print(role_element.get_attribute("class"))
        # post_elements = role_element.find_elements(By.XPATH, ".//div")
        # print(len(post_elements))
        
        # for post_element in post_elements[4:7]:
        #     # get class name of post element
        #     post_class = post_element.get_attribute("class")
        #     print(post_class)
            


            # traverse div/div/div/div/div/div/div/div/div
            # for _ in range(8):
            #     post_element = post_element.find_elements(By.XPATH, ".//div")
            #     print(post_element)
            #     if len(post_element) == 0:
            #         break
            #     post_element = post_element[0]
            # print(post_element)
            # print("#############################################################")
