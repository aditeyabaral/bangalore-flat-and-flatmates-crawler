import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData, Table

load_dotenv()


class FlatAndFlatmatesDatabase:
    def __init__(self):
        self.base = declarative_base()
        self.engine = create_engine(os.environ.get("DATABASE_URL"))
        self.connection = self.engine.connect()
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.setup_db()

        self.posts_table = Table(
            "post", self.metadata, autoload=True, autoload_with=self.engine
        )

    def setup_db(self):
        with open("conf/ddl.sql") as f:
            queries = f.read().strip().split("\n\n")
            for query in queries:
                try:
                    self.connection.execute(query)
                except Exception as e:
                    print(f"Error while executing query: {query}: {e}")

    def add_new_post_entry(self, create_time, content, keywords, filters, links):
        if not self.check_content_exists_in_db(content):
            query = self.posts_table.insert().values(
                create_time=create_time,
                content=content,
                keywords=keywords,
                filters=filters,
                links=links,
            )
            self.connection.execute(query)

    def get_all_post_entries(self):
        query = self.posts_table.select()
        return self.connection.execute(query).fetchall()

    def check_content_exists_in_db(self, content):
        query = self.posts_table.select().where(
            self.posts_table.c.content == content
        )
        return bool(self.connection.execute(query).fetchall())
