import time
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
    logging.info(f"Found {len(posts)} posts")
    logging.debug(f"Before processing: {posts}")
    posts = processor.process(posts)
    logging.debug(f"After processing: {posts}")
    logging.info("Inserting posts into database")
    for post in posts:
        db.add_new_post_entry(post)


def fetch_latest_posts():
    logging.info(f"Fetching new posts from groups")
    group_ids = processor.search_config["groups"]
    for group_id in group_ids:
        logging.info(f"Fetching latest posts from {group_id}")
        fetch_latest_posts_from_group(group_id)
        time.sleep(10)


if __name__ == "__main__":
    logging.info("Starting Facebook Group Crawler")
    crawler = Crawler()
    processor = Processor()
    CONFIG = processor.load_search_config("conf/search_config.json")
    processor.set_search_config(CONFIG)
    db = FlatAndFlatmatesDatabase()

    logging.info("Loading search config")
    search_config = processor.load_search_config()
    logging.debug(search_config)
    processor.set_search_config(search_config)

    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_latest_posts, "interval", minutes=20)
    logging.info("Starting scheduler for fetching new posts")
    scheduler.start()

    try:
        while True:
            time.sleep(1e4)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutting down Facebook Group Crawler")
        scheduler.shutdown()
