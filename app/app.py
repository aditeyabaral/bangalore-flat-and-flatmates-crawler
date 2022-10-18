import time
import json
import logging
from crawler import Crawler
from processor import Processor
from db import FlatAndFlatmatesDatabase
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    format="%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s",
    filemode="w",
)


def fetch_latest_posts_from_group(group_id):
    posts = crawler.crawl_posts_from_group(group_id, CONFIG.get("pages", 4))
    logging.debug(posts)
    logging.info(f"Found {len(posts)} posts")

    posts = processor.process(posts)
    logging.info(f"Length of posts after processing: {len(posts)}")
    json.dump(posts, open("posts.json", "w"), indent=4, default=str)


def fetch_latest_posts():
    logging.info(f"Fetching new posts from groups")
    group_ids = processor.search_config["groups"]
    for group_id in group_ids:
        logging.info(f"Fetching latest posts from {group_id}")
        fetch_latest_posts_from_group(group_id)
        time.sleep(10)
        break


if __name__ == "__main__":
    logging.info("Starting Facebook Group Crawler")
    crawler = Crawler()
    processor = Processor()
    CONFIG = processor.load_search_config("conf/search_config.json")
    processor.set_search_config(CONFIG)
    # db = FlatAndFlatmatesDatabase()

    logging.info("Loading search config")
    search_config = processor.load_search_config()
    logging.debug(search_config)
    processor.set_search_config(search_config)

    fetch_latest_posts()
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(fetch_latest_posts, "interval", minutes=15)
    # logging.info("Starting scheduler for fetching new posts")
    # scheduler.start()

    # try:
    #     while True:
    #         time.sleep(1e4)
    # except (KeyboardInterrupt, SystemExit):
    #     logging.info("Shutting down Facebook Group Crawler")
    #     scheduler.shutdown()
