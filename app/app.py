import logging

logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    format="%(asctime)s - %(levelname)s - %(pathname)s:%(lineno)d - %(funcName)s - %(message)s",
    filemode="w",
)

import os
import pytz
import time
import datetime
from driver import Driver
from processor import Processor
from db import FlatAndFlatmatesDatabase
from apscheduler.schedulers.background import BackgroundScheduler

IST = pytz.timezone("Asia/Kolkata")


def fetch_new_posts():
    logging.info(f"Fetching new posts at {datetime.datetime.now(IST)}")
    group_names = processor.search_config["groups"]
    for group_name in group_names:
        logging.info(f"Fetching posts from {group_name}")
        driver.create_driver()
        driver.open_facebook()
        driver.login_facebook(facebook_username, facebook_password)
        driver.visit_group(group_name)

        logging.info("Scraping posts")
        results = driver.scrape_posts_on_page()
        logging.info(f"Found {len(results)} posts")
        logging.debug(results)

        results, keywords, filter_checks = processor.process(results)
        for result, keyword, filter_check in zip(results, keywords, filter_checks):
            content = result["content"]
            create_time = result["create_time"]
            links = ",".join(result["links"])
            # db.add_new_post_entry(create_time, content, keyword, filter_check, links)
        driver.destroy_driver()
        time.sleep(10)


if __name__ == "__main__":
    logging.info("Starting Facebook Group Crawler")
    driver = Driver()
    processor = Processor()
    # db = FlatAndFlatmatesDatabase()

    logging.info("Loading search config")
    search_config = processor.load_search_config()
    logging.debug(search_config)
    processor.set_search_config(search_config)

    facebook_username = os.environ["FACEBOOK_USERNAME"]
    facebook_password = os.environ["FACEBOOK_PASSWORD"]
    # driver.open_facebook()
    # driver.login_facebook(facebook_username, facebook_password)

    fetch_new_posts()
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(fetch_new_posts, "interval", minutes=15)
    # scheduler.start()

    # try:
    #     while True:
    #         pass
    # except (KeyboardInterrupt, SystemExit):
    #   logging.info("Shutting down Facebook Group Crawler")
    #     scheduler.shutdown()
    #     driver.chrome.quit()
