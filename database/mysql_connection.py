import os
import logging
import pymysql
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


if len(logging.getLogger().handlers) > 0:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)


class ConnectDB:
    def __init__(self, autocommit=True):
        try:
            print("Connecting to DB using PyMySQL...")

            self.conn = pymysql.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USERNAME"),
                password=os.getenv("DB_PASSWORD"),
                db=os.getenv("DB_DATABASE"),
                charset=os.getenv("DB_CHARSET", "utf8"),
                port=int(os.getenv("DB_PORT"))
            )


            self.conn.autocommit(autocommit)
            self.cursor = self.conn.cursor()

            print("✅ DB Connection Successful (PyMySQL)")
            logging.info("Database connection established")

        except Exception as err:
            print("❌ DB Connection Failed:", err)
            logging.error(f"DB connection failed: {err}")

    # ---------------------------------------------
    # FETCH + PRINT SHAPE + RETURN DATAFRAME
    # ---------------------------------------------
    def execute(self, query):
        try:
            response = {
                        "status_code": 500,
                        "status": "failed",
                        "message": None
                        }
            self.cursor.execute(query)
            self.conn.commit()
            response = {
                        "status_code": 200,
                        "status": "success",
                        "message": "Query executed successfully"
                        }
            logging.info(f"Query executed successfully")
        except Exception as err:
            logging.exception(f"Something went wrong in executing query - ConnectDB.execute(): {err}")
        finally:
            return response
        
    def fetch(self, query):
        try:
            response = {
                        "status_code": 500,
                        "status": "failed",
                        "data": None,
                        "message": None
                        }
            self.cursor.execute(query)
            # for query in query_dict:
            #     self.cursor.execute(query["query"], query["data"])
            rows = self.cursor.fetchall()
            if self.cursor.description is not None:
                columns = [col[0] for col in self.cursor.description]
                result = [dict(zip(columns, row)) for row in rows]
                # self.table = pd.DataFrame(database_table, columns=columns)
                logging.info(f'{len(result)} rows fetched')
                response = {
                        "status_code": 200,
                        "status": "success",
                        "data": result,
                        "message": "Entries fetched successfully"
                        }
        except Exception as err:
            logging.exception(f"Something went wrong in executing query {query} ConnectDB.fetch(): {err}")
        finally:
            return response
        
    def insert(self, query_dict, autocommit: bool = False):
        try:
            response = {
                        "status_code": 500,
                        "status": "failed",
                        "message": None
                        }
            self.conn.autocommit = autocommit
            for query in query_dict:
                self.cursor.execute(query["query"], query["data"])
            self.conn.commit()
            response = {
                        "status_code": 200,
                        "status": "success",
                        "message": "Entry inserted successfully"
                        }
            logging.info(f"Entry inserted successfully")
        except Exception as err:
            self.conn.rollback()
            logging.exception(f"Something went wrong in inserting entry - ConnectDB.insert(): {err}")
        finally:
            self.conn.autocommit = True
            return response

    def update(self, query_dict, autocommit: bool = False):
        try:
            response = {
                        "status_code": 500,
                        "status": "failed",
                        "message": None
                        }
            self.conn.autocommit = autocommit
            for query in query_dict:
                self.cursor.execute(query["query"], query["data"])
            self.conn.commit()
            response = {
                        "status_code": 200,
                        "status": "success",
                        "message": "Entry updated successfully"
                        }
            logging.info(f"Entry updated successfully")
        except Exception as err:
            logging.exception(f"Something went wrong in updating entry - ConnectDB.update(): {err}")
        finally:
            self.conn.autocommit = True
            return response

    def close_connection(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.conn is not None:
            self.conn.close()
        logging.info('Database connection closed')
