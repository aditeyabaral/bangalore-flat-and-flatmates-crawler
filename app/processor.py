import re
import json
import editdistance


class Processor:
    def __init__(self):
        self.search_config = None

    def set_search_config(self, search_config):
        self.search_config = search_config
    
    @staticmethod
    def load_search_config():
        with open("conf/search_config.json") as f:
            return json.load(f)

    def clean_content(self, content):
        content = re.sub(r"[^\w\s]", " ", content)
        content = re.sub(r"\s+", " ", content)
        content = content.lower()
        return content

    def find_exact_keywords(self, data):
        content = data["content"].lower()
        keywords_to_search = self.search_config["keywords"]
        keywords_found = list()
        for keyword in keywords_to_search:
            if keyword in content:
                keywords_found.append(keyword)
        return keywords_found

    def find_similar_keywords(self, data, threshold=3):
        content = self.clean_content(data["content"])
        keywords_to_search = self.search_config["similar_keywords"]
        keywords_found = list()
        content_words = content.split()
        for keyword in keywords_to_search:
            for content_word in content_words:
                if editdistance.eval(keyword, content_word) <= threshold:
                    keywords_found.append(keyword)
                    break
        return keywords_found

    def check_filters(self, data, threshold=3):
        content = self.clean_content(data["content"])
        filters_to_check = self.search_config["similar_keywords"]
        content_words = content.split()
        for filter_word in filters_to_check:
            for content_word in content_words:
                if editdistance.eval(filter_word, content_word) <= threshold:
                    return True
        return False

    def filter_duplicate_results(self, results):
        covered_contents = list()
        filtered_results = list()
        for result in results:
            if result["content"] not in covered_contents:
                filtered_results.append(result)
                covered_contents.append(result["content"])
        return filtered_results
