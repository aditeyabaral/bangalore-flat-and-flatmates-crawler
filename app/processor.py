import re
import json
import logging
import editdistance


class Processor:
    def __init__(self):
        self.search_config = None

    def set_search_config(self, search_config):
        logging.info("Setting search config")
        self.search_config = search_config

    @staticmethod
    def load_search_config(filepath="conf/search_config.json"):
        logging.info(f"Loading search config from {filepath}")
        try:
            with open(filepath) as f:
                data = json.load(f)
            logging.debug(data)
            return data
        except Exception as e:
            logging.error(f"Error while loading search config: {e}")
            return None

    def clean_content(self, content):
        logging.debug(f"Cleaning content in content: {content}")
        content = re.sub(r"[^\w\s]", " ", content)
        content = re.sub(r"\s+", " ", content)
        content = content.lower()
        return content

    def find_exact_keywords(self, data):
        logging.debug("Finding exact keywords in data: {data}")
        content = data["content"].lower()
        keywords_to_search = self.search_config["keywords"]
        keywords_found = list()
        for keyword in keywords_to_search:
            if keyword in content:
                keywords_found.append(keyword)
        return keywords_found

    def find_similar_keywords(self, data, threshold=2):
        logging.debug(f"Finding similar keywords with threshold = {threshold} in data: {data}")
        content = self.clean_content(data["content"])
        keywords_to_search = self.search_config["keywords"]
        keywords_found = list()
        content_words = content.split()
        for keyword in keywords_to_search:
            for content_word in content_words:
                if editdistance.eval(keyword, content_word) <= threshold:
                    keywords_found.append(keyword)
                    break
        return keywords_found

    def check_filters(self, data, threshold=2):
        logging.debug(f"Checking filters with threshold = {threshold} in data: {data}")
        content = self.clean_content(data["content"])
        filters_to_check = self.search_config["filters"]
        content_words = content.split()
        for filter_word in filters_to_check:
            for content_word in content_words:
                if editdistance.eval(filter_word, content_word) <= threshold:
                    return True
        return False

    def filter_duplicate_results(self, results):
        logging.debug("Filtering duplicate results")
        covered_contents = list()
        filtered_results = list()
        for result in results:
            if result["content"] not in covered_contents:
                filtered_results.append(result)
                covered_contents.append(result["content"])
        return filtered_results

    def process(self, results):
        logging.info("Processing results")
        results = self.filter_duplicate_results(results)
        exact_keywords = list(map(self.find_exact_keywords, results))
        similar_keywords = list(map(self.find_similar_keywords, results))
        keywords = list(
            map(lambda x, y: ",".join(x + y), exact_keywords, similar_keywords)
        )
        filter_checks = list(map(self.check_filters, results))
        return results, keywords, filter_checks
