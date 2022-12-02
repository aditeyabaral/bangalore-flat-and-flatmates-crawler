import logging
import os
import time
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from typing import Tuple, List, Dict, Any
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

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

    def add_new_post_entry(self, post: Dict[str, Any]):
        try:
            query = (
                insert(self.posts_table)
                .values(post)
                .on_conflict_do_nothing(index_elements=["text"])
            )
            self.connection.execute(query)
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
