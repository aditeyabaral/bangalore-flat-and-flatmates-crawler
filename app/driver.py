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
        self.chrome_options.add_argument("--start-maximized")
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

    # /div/div[2]/div/div[2]/span/span/span[2]/span/a
    def parse_header_element(self, header_element):
        # anchor_and_time_element = header_element.find_element(By.XPATH, "./div/div[2]/div/div[2]/span/span/span[2]/span/a")
        # print(anchor_and_time_element.get_attribute("class"))
        # print(anchor_and_time_element.get_attribute("href"))
        # print(anchor_and_time_element.find_element(By.XPATH, "./span").text)


        anchor_tags = header_element.find_elements(By.XPATH, ".//a[@role=\"link\"]")
        links = set()
        for anchor_tag in anchor_tags:
            url = anchor_tag.get_attribute("href")
            print(url)
            url = url.split("?")[0]
            # if "user" in url:
            links.add(url)
        print("Links:", links)

        # span_tags = header_element.find_elements(By.XPATH, ".//span")
        # for span_tag in span_tags:
        #     print(span_tag.text)

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
        url = f"https://www.facebook.com/groups/{group_name}?sorting_setting=CHRONOLOGICAL_LISTINGS"
        self.chrome.get(url)

    def scrape_posts_on_page(self):
        time.sleep(4)
        for _ in range(5):
            ActionChains(self.chrome).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(0.5)
        time.sleep(2)

        feed_xpath = "/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div[4]/div/div/div[2]/div/div/div[1]/div[2]/div[3]"
        feed_element = self.chrome.find_element(By.XPATH, feed_xpath)

        post_elements = feed_element.find_elements(By.XPATH, "./div")[2:]
        print(len(post_elements))

        for post_element in post_elements[:5]:
            print("Class of post element:", post_element.get_attribute("class"))
            content = str()
            current_post_elements = post_element.find_elements(By.XPATH, "./div/div/div/div/div/div/div/div/div/div")[1:]
            current_post_elements = list(filter(lambda x: x.get_attribute("class").strip() == "", current_post_elements))
            current_post_elements = current_post_elements[0].find_elements(By.XPATH, "./div/div")
            num_current_post_elements = len(current_post_elements)
            print("Number of current_post_elements:", num_current_post_elements)
            _, header_element, body_element, comment_element = current_post_elements
            self.parse_header_element(header_element)
            break