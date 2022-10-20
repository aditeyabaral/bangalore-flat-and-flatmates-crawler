import os
import time
import logging
from dotenv import load_dotenv
from typing import Tuple, List, Dict
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData, Table

load_dotenv()


class FlatAndFlatmatesDatabase:
    def __init__(self):

        while True:
            try:
                logging.info("Trying to connect to database")
                self.base = declarative_base()
                self.engine = create_engine(os.environ.get("DATABASE_URL"))
                self.connection = self.engine.connect()
                self.metadata = MetaData()
                self.Session = sessionmaker(bind=self.engine)
                self.session = self.Session()
                self.connection.execute("SELECT 1")
                logging.info("Connected to database successfully")
                break
            except Exception as e:
                logging.error(f"Error while connecting to database: {e}")
                logging.info("Retrying database connection in 5 seconds")
                time.sleep(5)

        self.setup_db()
        self.posts_table = Table(
            "post", self.metadata, autoload=True, autoload_with=self.engine
        )

    def setup_db(self):
        logging.info("Setting up database tables")
        with open("conf/ddl.sql") as f:
            queries = f.read().strip().split("\n\n")
            for query in queries:
                logging.debug(query)
                try:
                    self.connection.execute(query)
                except Exception as e:
                    logging.error(f"Error while executing query: {query}: {e}")

    def add_new_post_entry(self, post: Dict):
        try:
            query = self.connection.execute(self.posts_table.insert(), post)
            logging.debug(query)
        except Exception as e:
            logging.error(f"Error while adding new post entry: {post}: {e}")

    def get_all_post_entries(self) -> List[Tuple]:
        try:
            query = self.posts_table.select()
            logging.debug(query)
            return self.connection.execute(query).fetchall()
        except Exception as e:
            logging.error(f"Error while getting all post entries: {e}")
            return list()

    def check_content_exists_in_db(self, content: str) -> bool:
        try:
            query = self.posts_table.select().where(
                self.posts_table.c.content == content
            )
            logging.debug(query)
            return bool(self.connection.execute(query).fetchall())
        except Exception as e:
            logging.error(
                f"Error while checking content exists in database: {content})\nError: {e}"
            )
            return False
