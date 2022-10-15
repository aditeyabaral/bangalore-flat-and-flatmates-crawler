import os
from driver import Driver
from db import FlatAndFlatmatesDatabase

if __name__ == "__main__":
    driver = Driver()
    # db = FlatAndFlatmatesDatabase()

    facebook_username = os.environ["FACEBOOK_USERNAME"]
    facebook_password = os.environ["FACEBOOK_PASSWORD"]

    driver.open_facebook()
    driver.login_facebook(facebook_username, facebook_password)
    group_name = "1019544874745682"
    driver.visit_group(group_name)
    driver.scrape_posts_on_page()
