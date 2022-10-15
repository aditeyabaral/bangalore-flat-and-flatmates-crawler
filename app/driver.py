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

    # TODO: Return create_time
    def parse_header_element(self, header_element):
        anchor_tags = header_element.find_elements(By.XPATH, ".//a[@role=\"link\"]")
        links = set()
        for anchor_tag in anchor_tags:
            try:
                ActionChains(self.chrome).move_to_element(anchor_tag).perform()
            except:
                pass
            time.sleep(0.5)
            url = anchor_tag.get_attribute("href")
            url = url.split("?")[0]
            if "posts" in url:
                links.add(url)
            try:
                span_element = anchor_tag.find_element(By.XPATH, "./span")
            except:
                pass
        return links

    def parse_body_element(self, body_element):
        buttons = body_element.find_elements(By.XPATH, ".//div[@role=\"button\"]")
        for button in buttons:
            if button.get_attribute("aria-label") != "Message":
                button.click()
        paragraph_elements = body_element.find_elements(By.XPATH, ".//div[@dir=\"auto\"]")
        content = str()
        for paragraph_element in paragraph_elements:
            content += paragraph_element.text.strip() + '\n'
        return content
        
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
        # time.sleep(4)
        for _ in range(10):
            ActionChains(self.chrome).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(1)
        time.sleep(2)

        feed_xpath = "/html/body/div[1]/div/div[1]/div/div[5]/div/div/div[3]/div/div/div[1]/div[1]/div/div[2]/div/div/div[4]/div/div/div[2]/div/div/div[1]/div[2]/div[3]"
        feed_element = self.chrome.find_element(By.XPATH, feed_xpath)

        post_elements = feed_element.find_elements(By.XPATH, "./div")[2:]

        for post_element in post_elements[:5]:
            content = str()
            current_post_elements = post_element.find_elements(By.XPATH, "./div/div/div/div/div/div/div/div/div/div")[1:]
            current_post_elements = list(filter(lambda x: x.get_attribute("class").strip() == "", current_post_elements))
            current_post_elements = current_post_elements[0].find_elements(By.XPATH, "./div/div")
            _, header_element, body_element, comment_element = current_post_elements
            links = self.parse_header_element(header_element)
            content = self.parse_body_element(body_element)
            print(content)
            print(links)
            print('#' * 90)