import json
import logging
import sqlite3
import threading
import os
import sys
from typing import Any, List, Dict, Optional, Tuple
from ..datamodel import Member

MEMBER_TABLE_SQL = """
            CREATE TABLE IF NOT EXISTS members (
                id TEXT NOT NULL,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                tags TEXT,
                UNIQUE (id)
            )
            """

lock = threading.Lock()
logger = logging.getLogger()

class DBManager:
    """
    A database manager class that handles the creation and interaction with an SQLite database.
    """

    def __init__(self, path: str = "database.sqlite", **kwargs: Any) -> None:
        """
        Initializes the DBManager object, creates a database if it does not exist, and establishes a connection.

        Args:
            path (str): The file path to the SQLite database file.
            **kwargs: Additional keyword arguments to pass to the sqlite3.connect method.
        """

        self.path = path
        # check if the database exists, if not create it
        # self.reset_db()
        if not os.path.exists(self.path):
            logger.info("Creating database")
            self.init_db(path=self.path, **kwargs)

        try:
            self.conn = sqlite3.connect(self.path, check_same_thread=False, **kwargs)
            self.cursor = self.conn.cursor()
        except Exception as e:
            logger.error("Error connecting to database: %s", e)
            raise e

    def reset_db(self):
        """
        Reset the database by deleting the database file and creating a new one.
        """
        print("resetting db")
        if os.path.exists(self.path):
            # os.remove(self.path)
            print ("will not reset db!!! Do it yourself!")
            sys.exit(1)
        self.init_db(path=self.path)

    def run_migrations(self):
        """
        Run migrations to update the database schema.
        """

        pass

    def init_db(self, path: str = "database.sqlite", **kwargs: Any) -> None:
        """
        Initializes the database by creating necessary tables.

        Args:
            path (str): The file path to the SQLite database file.
            **kwargs: Additional keyword arguments to pass to the sqlite3.connect method.
        """
        # Connect to the database (or create a new one if it doesn't exist)
        self.conn = sqlite3.connect(path, check_same_thread=False, **kwargs)
        self.cursor = self.conn.cursor()

        # Create the models table
        self.cursor.execute(MEMBER_TABLE_SQL)

        # Commit the changes and close the connection
        self.conn.commit()

    def query(self, query: str, args: Tuple = (), return_json: bool = False) -> List[Dict[str, Any]]:
        """
        Executes a given SQL query and returns the results.

        Args:
            query (str): The SQL query to execute.
            args (Tuple): The arguments to pass to the SQL query.
            return_json (bool): If True, the results will be returned as a list of dictionaries.

        Returns:
            List[Dict[str, Any]]: The result of the SQL query.
        """
        try:
            with lock:
                self.cursor.execute(query, args)
                result = self.cursor.fetchall()
                self.commit()
                if return_json:
                    result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]
                return result
        except Exception as e:
            logger.error("Error running query with query %s and args %s: %s", query, args, e)
            raise e

    def commit(self) -> None:
        """
        Commits the current transaction Modelto the database.
        """
        self.conn.commit()

    def close(self) -> None:
        """
        Closes the database connection.
        """
        self.conn.close()

def get_item_by_field(table: str, field: str, value: Any, dbmanager: DBManager) -> Optional[Dict[str, Any]]:
    query = f"SELECT * FROM {table} WHERE {field} = ?"
    args = (value,)
    result = dbmanager.query(query=query, args=args)
    return result[0] if result else None

def update_item(table: str, item_id: str, updated_data: Dict[str, Any], dbmanager: DBManager) -> None:
    set_clause = ", ".join([f"{key} = ?" for key in updated_data.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
    args = (*updated_data.values(), item_id)
    dbmanager.query(query=query, args=args)

def upsert_member(member: Member, dbmanager: DBManager) -> Member:
    """
    Insert or update a member in the database.

    Args:
        member: The Member object containing member data
        dbmanager: The DBManager instance to interact with the database

    Returns:
        The inserted or updated Member object
    """

    # Check if the member with the provided id already exists in the database
    existing_member = get_item_by_field("members", "id", member.id, dbmanager)

    if existing_member:
        # If the member exists, update it with the new data
        updated_data = {
            "firstname": member.firstname,
            "lastname": member.lastname,
            "email": member.email,
            "phone": member.phone,
            "timestamp": member.timestamp,
            "tags": member.tags,
        }
        update_item("members", member.id, updated_data, dbmanager)
    else:
        # If the member does not exist, insert a new one
        query = """
            INSERT INTO members (id, firstname, lastname, email, phone, timestamp, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        args = (
            member.id,
            member.firstname,
            member.lastname,
            member.email,
            member.phone,
            member.timestamp,
            member.tags,
        )
        dbmanager.query(query=query, args=args)

    # Return the inserted or updated member
    return member
