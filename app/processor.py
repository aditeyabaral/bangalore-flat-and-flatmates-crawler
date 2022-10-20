import re
import json
import logging
import editdistance
from typing import Union, List, Dict


class Processor:
    def __init__(self):
        self.CONFIG = None

    def set_config(self, search_config: Dict):
        logging.info("Setting search config")
        self.CONFIG = search_config

    def load_config(
        self, filepath: str = "conf/search_config.json"
    ) -> Union[Dict, None]:
        logging.info(f"Loading search config from {filepath}")
        try:
            with open(filepath) as f:
                search_config = json.load(f)
            logging.debug(search_config)
            self.CONFIG = search_config
            return self.CONFIG
        except Exception as e:
            logging.error(f"Error while loading search config: {e}")
            return None

    def clean_text_content(self, post_data_text: str) -> str:
        logging.debug(f"Cleaning text content in post: {post_data_text}")
        post_data_text = re.sub(r"[^\w\s]", " ", post_data_text)
        post_data_text = re.sub(r"\s+", " ", post_data_text)
        post_data_text = post_data_text.lower()
        return post_data_text

    def extract_number_from_listing_price(
        self, listing_price: str
    ) -> Union[float, None]:
        logging.debug(f"Extracting number from listing price: {listing_price}")
        listing_price = re.sub(r"[^\d]", "", listing_price)
        if not listing_price:
            return None
        return float(listing_price)

    def convert_facebook_url_to_desktop_url(self, url: str) -> str:
        logging.debug(f"Converting facebook url to desktop url: {url}")
        return url.replace("m.facebook.com", "www.facebook.com")

    def find_exact_words(
        self, post_data_text: str, search_words: List[str], lowercase: bool = True
    ) -> List[str]:
        logging.debug(
            f"Finding exact matches for {search_words} in text: {post_data_text} with lowercase = {lowercase}"
        )
        if lowercase:
            post_data_text = post_data_text.lower()
        search_words_found = set()
        for search_word in search_words:
            if search_word in post_data_text:
                search_words_found.add(search_word)
        search_words_found = list(search_words_found)
        return search_words_found

    def find_similar_words(
        self,
        post_data_text: str,
        search_words: List[str],
        lowercase: bool = True,
        threshold: int = 2,
    ) -> List[str]:
        logging.debug(
            f"Finding similar matches for {search_words} with threshold = {threshold} in text: {post_data_text}"
        )
        if lowercase:
            post_data_text = post_data_text.lower()
        post_data_text_words = self.clean_text_content(post_data_text).split()
        similar_words_found = set()
        for search_word in search_words:
            for content_word in post_data_text_words:
                if editdistance.eval(search_word, content_word) <= threshold:
                    similar_words_found.add(search_word)
                    break
        similar_words_found = list(similar_words_found)
        return similar_words_found

    def filter_duplicate_results(self, posts: List[Dict]) -> List[Dict]:
        logging.debug("Filtering duplicate results")
        covered_post_text = list()
        filtered_posts = list()
        for post in posts:
            post_data_text = post.get("post_text", post.get("text", "")).strip()
            if post_data_text not in covered_post_text:
                filtered_posts.append(post)
                covered_post_text.append(post_data_text)
        return filtered_posts

    def extract_required_fields(self, post_data: Dict) -> Dict:
        required_fields = self.CONFIG.get("fields", [])
        required_fields = list(map(lambda field: field.split(":")[0], required_fields))
        logging.debug(f"Extracting required fields: {required_fields}")
        filtered_post_data = dict()
        for field in required_fields:
            if field == "post_url":
                filtered_post_data[field] = self.convert_facebook_url_to_desktop_url(
                    post_data.get(field, "")
                )
            elif field == "listing_price":
                filtered_post_data[field] = self.extract_number_from_listing_price(
                    post_data.get(field, "")
                )
            else:
                filtered_post_data[field] = post_data.get(field, None)
        return filtered_post_data

    def rename_required_fields_for_db_entry(self, post_data: Dict) -> Dict:
        required_fields = self.CONFIG.get("fields", [])
        logging.debug(f"Renaming required fields for db entry: {required_fields}")
        renamed_post_data = dict()
        for field in required_fields:
            post_field_name, db_field_name = field.split(":")
            renamed_post_data[db_field_name] = post_data.get(post_field_name, None)
        return renamed_post_data

    def process(self, posts: List[Dict]) -> List[Dict]:
        logging.info(f"Processing posts")
        posts = self.filter_duplicate_results(posts)
        posts = list(map(self.extract_required_fields, posts))

        exact_keywords = list(
            map(
                lambda post: self.find_exact_words(
                    post.get("post_text", post.get("text", "")),
                    self.CONFIG.get("keywords", []),
                    lowercase=True,
                ),
                posts,
            )
        )

        similar_keywords = list(
            map(
                lambda post: self.find_similar_words(
                    post.get("post_text", post.get("text", "")),
                    self.CONFIG.get("keywords", []),
                    lowercase=True,
                    threshold=self.CONFIG.get("spelling", 2),
                ),
                posts,
            )
        )

        keywords = list(
            map(
                lambda exact_keyword_list, similar_keyword_list: list(
                    set(exact_keyword_list + similar_keyword_list)
                ),
                exact_keywords,
                similar_keywords,
            )
        )

        filters = list(
            map(
                lambda post: bool(
                    self.find_exact_words(
                        post.get("post_text", post.get("text", "")),
                        self.CONFIG.get("filters", []),
                        lowercase=True,
                    )
                ),
                posts,
            )
        )

        posts = list(
            map(
                lambda post, keyword_list, filter_list: {
                    **post,
                    "keywords": keyword_list,
                    "filters": filter_list,
                },
                posts,
                keywords,
                filters,
            )
        )

        posts = list(map(self.rename_required_fields_for_db_entry, posts))
        posts = sorted(
            posts,
            key=lambda post: post.get("time", None),
            reverse=True,
        )

        return posts
