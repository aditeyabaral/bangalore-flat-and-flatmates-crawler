import os
import pytz
import time
import logging
import datetime
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

IST = pytz.timezone("Asia/Kolkata")


class Driver:
    def create_driver(self):
        logging.info("Creating driver")
        self.chrome_options = webdriver.ChromeOptions()
        # self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
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
            logging.debug(f"Chromedriver path: {chromedriver_path}")

            self.chrome = webdriver.Chrome(
                executable_path=chromedriver_path, options=self.chrome_options
            )
        self.chrome.execute_cdp_cmd(
            "Emulation.setTimezoneOverride", {"timezoneId": "Asia/Kolkata"}
        )

    def destroy_driver(self):
        self.chrome.quit()

    def get_driver(self):
        return self.chrome

    def scroll_facebook(self, num_pages=1):
        logging.info(f"Scrolling {num_pages} pages")
        for _ in range(num_pages):
            ActionChains(self.chrome).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(1)

    def get_post_elements(self):
        try:
            WebDriverWait(self.chrome, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
            )
            feed_element = self.chrome.find_element(By.XPATH, '//div[@role="feed"]')
            post_elements = feed_element.find_elements(By.XPATH, "./div")[1:]
            return post_elements
        except Exception as e:
            logging.error(f"Could not find feed element")
        return list()

    # TODO: Return create_time
    def parse_header_element(self, header_element):
        anchor_tags = header_element.find_elements(By.XPATH, './/a[@role="link"]')
        links = set()
        for anchor_tag in anchor_tags:
            try:
                ActionChains(self.chrome).move_to_element(anchor_tag).perform()
            except Exception as e:
                logging.error(f"Could not move to element")
            # time.sleep(0.2)
            url = anchor_tag.get_attribute("href")
            url = url.split("?")[0]
            if "posts" in url:
                links.add(url)
        links = list(links)
        return links

    def parse_body_element(self, body_element):
        buttons = body_element.find_elements(By.XPATH, './/div[@role="button"]')
        for button in buttons:
            if button.get_attribute("aria-label") != "Message":
                button.click()
        paragraph_elements = body_element.find_elements(By.XPATH, './/div[@dir="auto"]')
        content = list()
        for paragraph_element in paragraph_elements:
            paragraph_text = paragraph_element.text.strip()
            if paragraph_text and paragraph_text not in content:
                content.append(paragraph_text)
        return "\n".join(content)

    def parse_post_elements(self, post_elements, max_retries=2):
        result = list()
        index = 0
        current_retry_count = 0
        total_post_elements = len(post_elements)
        while current_retry_count < max_retries and index < total_post_elements:
            try:
                post_element = post_elements[index]
                current_post_elements = post_element.find_elements(
                    By.XPATH, "./div/div/div/div/div/div/div/div/div/div"
                )[1:]
                current_post_elements = list(
                    filter(
                        lambda x: x.get_attribute("class").strip() == "",
                        current_post_elements,
                    )
                )
                current_post_elements = current_post_elements[0].find_elements(
                    By.XPATH, "./div/div"
                )
                num_current_post_elements = len(current_post_elements)
                header_element = current_post_elements[1]
                body_element = current_post_elements[2]
                links = self.parse_header_element(header_element)
                content = self.parse_body_element(body_element)
                if content != "":
                    result.append(
                        {
                            "links": links,
                            "content": content,
                            "create_time": str(datetime.datetime.now(IST)),
                        }
                    )
                index += 1
            except StaleElementReferenceException as e:
                logging.error(f"Stale element reference exception")
                if current_retry_count >= max_retries - 1:
                    logging.info(f"Max retries reached. Skipping post element {index}")
                    index += 1
                else:
                    logging.info(f"Retrying post element {index}")
                    current_retry_count += 1
                    # index = 0
                    post_elements = self.get_post_elements()
                    total_post_elements = len(post_elements)
                    continue
            except Exception as e:
                logging.error(f"Could not parse post element")
                index += 1

        return result

    def open_facebook(self):
        self.chrome.get("https://www.facebook.com/login/")

    def login_facebook(self, username, password):
        if self.chrome.current_url != "https://www.facebook.com/login/":
            raise ("Facebook is not open. Use open_facebook() to open Facebook first.")

        WebDriverWait(self.chrome, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="email"]'))
        )
        email_input = self.chrome.find_element(By.XPATH, '//*[@id="email"]')
        password_input = self.chrome.find_element(By.XPATH, '//*[@id="pass"]')
        email_input.send_keys(username)
        password_input.send_keys(password)
        self.chrome.find_element(By.XPATH, "//button[@type='submit']").click()

    def visit_group(self, group_name):
        time.sleep(1)
        url = f"https://www.facebook.com/groups/{group_name}?sorting_setting=CHRONOLOGICAL_LISTINGS"
        self.chrome.get(url)
        time.sleep(3)

    def scrape_posts_on_page(self):
        results = list()
        for i in range(3):
            logging.info(f"Scraping page {i+1}")
            post_elements = self.get_post_elements()
            results.extend(self.parse_post_elements(post_elements))
            self.scroll_facebook(2)
        return results
