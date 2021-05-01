from instagram import Instagram
from typing import Any

import time
import os
import pickle


class Utils:
    """
    This class contains all the helper functions needed
    to create, load files and communicate with the database"""

    def __init__(self, cursor):
        self.cursor = cursor

    def save_file(self, links: list, filename: str) -> None:
        """Saves a python object with passed `filename`"""
        with open(filename, "wb") as filehandler:

            pickle.dump(links, filehandler)

    def load_file(self, filename: str, username: str) -> dict:
        """Loads a python object stored in `filename`"""

        # If there is not file, create it with an empty dict
        if not os.path.exists(filename):
            with open(filename, "wb") as filehandle:
                pending_tasks = dict()
                pending_tasks[username] = set()
                pickle.dump(pending_tasks, filehandle)

        with open(filename, "rb") as filehandle:

            pending_tasks = pickle.load(filehandle)

            return pending_tasks

    def select_users(self, table: str = "User") -> set:
        self.cursor.execute(f"SELECT username FROM {table};")
        following = self.cursor.fetchall()
        following = {row[0] for row in following}

        return following

    def select_followees(self, table: str, username: str) -> set:
        """
        Returns the accounts that `username` is already following
        or have previously visited. Else return an empty set.

        Table = Following or Visited
        """
        self.cursor.execute(
            f"SELECT username FROM {table} WHERE followed_by = '{username}';"
        )
        accounts = self.cursor.fetchall()

        if len(accounts) < 1:
            following = set()
            return following
        else:
            following = {row[0] for row in accounts}
            return following

    def insert_user(self, username: str) -> None:
        query = f"INSERT INTO User (username) values (?);"
        self.cursor.execute(query, (username,))

    def insert_followed_or_visited_account(
        self, table: str, username: str, followed_by: str, photos_liked: int = None
    ) -> None:
        if table == "Following":
            query = f"INSERT INTO Following (username, followed_by) values (?, ?);"
            self.cursor.execute(query, (username, followed_by))
        elif table == "Visited":
            query = f"INSERT INTO Visited (username, photos_liked, followed_by) values (?, ?, ?);"
            self.cursor.execute(query, (username, photos_liked, followed_by))

    def insert_photos(self, link, liked_by):
        query = f"INSERT INTO Photos (link, liked_by) values (?, ?);"
        self.cursor.execute(query, (link, liked_by))


if __name__ == "__main__":
    pass
