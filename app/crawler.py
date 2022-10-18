import random
import logging
import facebook_scraper


class Crawler:
    def __init__(
        self,
        options={"comments": False, "reactors": False, "allow_extra_requests": False},
    ):
        logging.info(f"Initializing crawler with options: {options}")
        self.options = options
        self.user_agents = [
            "Mozilla/5.0 (Linux; U; Android 10; SM-G960F Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.50 Mobile Safari/537.36 OPR/60.0.2254.59405",
        ]

    def crawl_posts_from_group(self, group_id, pages=4):
        logging.info(f"Fetching {pages} pages of posts from group {group_id}")
        user_agent = random.choice(self.user_agents)
        logging.info(f"Using user agent: {user_agent}")
        facebook_scraper.set_user_agent(user_agent)
        posts = list(
            facebook_scraper.get_posts(
                group=f"{group_id}?sorting_setting=CHRONOLOGICAL_LISTINGS",
                pages=pages,
                options=self.options,
            )
        )
        return posts

    def crawl_posts_from_post_urls(self, post_urls):
        logging.info(f"Fetching posts from urls: {post_urls}")
        user_agent = random.choice(self.user_agents)
        logging.info(f"Using user agent: {user_agent}")
        facebook_scraper.set_user_agent(user_agent)
        if isinstance(post_urls, str):
            post_urls = [post_urls]
        posts = list(
            facebook_scraper.get_posts(post_urls=post_urls, options=self.options)
        )
        return posts
