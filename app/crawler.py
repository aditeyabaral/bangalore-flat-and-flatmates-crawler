import random
import facebook_scraper


class Crawler:
    def __init__(
        self,
        options={"comments": False, "reactors": False, "allow_extra_requests": False},
    ):
        self.options = options
        self.user_agents = [
            "Mozilla/5.0 (Linux; U; Android 10; SM-G960F Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/95.0.4638.50 Mobile Safari/537.36 OPR/60.0.2254.59405",
        ]

    def crawl_posts_from_group(self, group_id, pages=4):
        facebook_scraper.set_user_agent(random.choice(self.user_agents))
        posts = list(
            facebook_scraper.get_posts(
                group=f"{group_id}?sorting_setting=CHRONOLOGICAL_LISTINGS",
                pages=pages,
                options=self.options,
            )
        )
        return posts

    def crawl_posts_from_post_urls(self, post_urls):
        facebook_scraper.set_user_agent(random.choice(self.user_agents))
        if isinstance(post_urls, str):
            post_urls = [post_urls]
        posts = list(
            facebook_scraper.get_posts(post_urls=post_urls, options=self.options)
        )
        return posts
