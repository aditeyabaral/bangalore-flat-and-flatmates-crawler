import os
import pytz
import time
import logging
from driver import Driver
from processor import Processor
from db import FlatAndFlatmatesDatabase
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    format="%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s",
    filemode="w",
)

IST = pytz.timezone("Asia/Kolkata")


def fetch_new_posts():
    logging.info(f"Fetching new posts from groups")
    group_names = processor.search_config["groups"]
    for group_name in group_names:
        logging.info(f"Fetching posts from {group_name}")
        driver.visit_group(group_name)

        logging.info("Scraping posts")
        results = driver.scrape_posts_on_page()
        logging.info(f"Found {len(results)} posts")
        logging.info(results)

        results, keywords, filter_checks = processor.process(results)
        for result, keyword, filter_check in zip(results, keywords, filter_checks):
            content = result["content"]
            create_time = result["create_time"]
            links = ",".join(result["links"])
            logging.debug(
                f"Inserting: ({content}, {create_time}, {links}, {keyword}, {filter_check})"
            )
            db.add_new_post_entry(create_time, content, keyword, filter_check, links)
        time.sleep(10)


if __name__ == "__main__":
    logging.info("Starting Facebook Group Crawler")
    driver = Driver()
    processor = Processor()
    db = FlatAndFlatmatesDatabase()

    logging.info("Loading search config")
    search_config = processor.load_search_config()
    logging.debug(search_config)
    processor.set_search_config(search_config)

    facebook_username = os.environ["FACEBOOK_USERNAME"]
    facebook_password = os.environ["FACEBOOK_PASSWORD"]
    driver.create_driver()
    driver.open_facebook()
    driver.login_facebook(facebook_username, facebook_password)

    # fetch_new_posts()
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_new_posts, "interval", minutes=15)
    logging.info("Starting scheduler for fetching new posts")
    scheduler.start()

    try:
        while True:
            time.sleep(1e4)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutting down Facebook Group Crawler")
        scheduler.shutdown()
        driver.destroy_driver()
