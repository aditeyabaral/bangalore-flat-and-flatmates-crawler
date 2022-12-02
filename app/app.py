import logging
import time
from apscheduler.schedulers.background import BackgroundScheduler
from concurrent.futures import ThreadPoolExecutor
from typing import Union, List, Dict, Any

from crawler import Crawler
from db import FlatAndFlatmatesDatabase
from processor import Processor

logging.basicConfig(
    level=logging.INFO,
    filename="app.log",
    format="%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(threadName)s:%(lineno)d - %(message)s",
    filemode="w",
)


def fetch_latest_posts_from_group(group_id: Union[str, int], num_pages: int = 1):
    logging.info(f"Fetching latest posts from {group_id}")
    posts: List[Dict] = crawler.crawl_posts_from_group(group_id, num_pages)
    logging.info(f"Found {len(posts)} posts")
    logging.debug(posts)
    posts: List[Dict] = processor.process(posts)
    logging.info(f"After processing, there are {len(posts)} posts")
    logging.info("Inserting posts into database")
    for post in posts:
        logging.debug(f"Inserting post {post}")
        db.add_new_post_entry(post)


def fetch_latest_posts():
    logging.info(f"Fetching new posts from groups")
    group_ids: List[str] = SEARCH_CONFIG.get("groups", [])
    num_pages: int = SEARCH_CONFIG.get("pages", 4)
    multithreading_flag: bool = SEARCH_CONFIG.get("multithreading", False)
    if multithreading_flag:
        num_group_ids = len(group_ids)
        num_pages_iterable = [num_pages] * num_group_ids
        with ThreadPoolExecutor(max_workers=num_group_ids) as executor:
            executor.map(
                fetch_latest_posts_from_group,
                group_ids,
                num_pages_iterable,
            )
    else:
        for group_id in group_ids:
            fetch_latest_posts_from_group(group_id, num_pages)
            time.sleep(10)


if __name__ == "__main__":
    logging.info("Starting Facebook Group Crawler")

    processor = Processor()
    SEARCH_CONFIG: Union[Dict[str, Any], None] = processor.load_config(
        "conf/search_config.json"
    )
    if not SEARCH_CONFIG:
        logging.error("Search config not found. Exiting.")
        exit(1)
    logging.debug(f"Loaded search_config: {SEARCH_CONFIG}")

    db = FlatAndFlatmatesDatabase()
    crawler = Crawler(
        SEARCH_CONFIG.get("crawler_options", Crawler.SCRAPER_DEFAULT_OPTIONS)
    )

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        fetch_latest_posts, "interval", minutes=SEARCH_CONFIG.get("interval", 20)
    )

    fetch_latest_posts()
    logging.info("Starting scheduler for fetching new posts")
    scheduler.start()

    try:
        while True:
            time.sleep(1e4)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutting down Facebook Group Crawler")
        scheduler.shutdown()
