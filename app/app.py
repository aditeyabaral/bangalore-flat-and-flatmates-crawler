import logging

logging.basicConfig(
    level=logging.NOTSET,
    filename="app.log",
    format="%(asctime)s - %(levelname)s - %(pathname)s:%(lineno)d - %(funcName)s - %(message)s",
    filemode="w",
)

import os
import time
from driver import Driver
from processor import Processor
from db import FlatAndFlatmatesDatabase
from apscheduler.schedulers.background import BackgroundScheduler

def process(results):
    results = processor.filter_duplicate_results(results)
    exact_keywords = list(map(processor.find_exact_keywords, results))
    similar_keywords = list(map(processor.find_similar_keywords, results))
    keywords = ",".join(list(set(exact_keywords + similar_keywords)))
    filter_checks = list(map(processor.check_filters, results))
    for result, keyword, filter_check in zip(results, keywords, filter_checks):
        content = result["content"]
        create_time = result["create_time"]
        links = ",".join(result["links"])
        db.add_new_post_entry(content, create_time, links, keyword, filter_check)

def fetch_new_posts():
    group_names = processor.search_config["groups"]
    for group_name in group_names:
        driver.visit_group(group_name)
        results = driver.scrape_posts_on_page()
        process(results)
        time.sleep(10)

if __name__ == "__main__":
    driver = Driver()
    processor = Processor()
    db = FlatAndFlatmatesDatabase()
    search_config = processor.load_search_config()
    processor.set_search_config(search_config)

    facebook_username = os.environ["FACEBOOK_USERNAME"]
    facebook_password = os.environ["FACEBOOK_PASSWORD"]
    driver.open_facebook()
    driver.login_facebook(facebook_username, facebook_password)

    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_new_posts, "interval", minutes=15)
    scheduler.start()

    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        driver.chrome.quit()
