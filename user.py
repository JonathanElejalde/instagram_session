from instagram import Instagram
from instagram import driver

import time
import os
import pickle


class User(Instagram):
    """This class will communicate with the database and will extend
        the Instagram class with all the functionality to navigate
        in Instagram like a regular user"""

    users_left_path = 'users_left.data'

    def save_users(self, links):
        with open(self.users_left_path, 'wb') as filehandle:

            # Store the data as a binary data stream
            pickle.dump(links, filehandle)

    def load_users(self):
        # If there is not file, create it with an empty list
        if not os.path.exists(self.users_left_path):
            with open(self.users_left_path, 'wb') as filehandle:
                empty_list = []
                pickle.dump(empty_list, filehandle)

        with open(self.users_left_path, 'rb') as filehandle:

            # Read the data as binary data stream
            users_left = pickle.load(filehandle)

            return users_left

    def already_follow(self, link):
        """Checks if we can or cannot follow the account

        Parameters
        ----------
        username : str
            The homepage link of the account

        Returns
        -------
        follow : boolean """

        driver.get(link)
        time.sleep(2)
        follow = False

        # We identify the follow button and then we decide what to do
        try:
            follow_button = driver.find_element_by_css_selector(".BY3EC")
            # Check for "Seguir" or "Follow". Depends on the user language
            if follow_button.text == "Seguir" or follow_button.text == "Follow":
                follow = True
                return follow
            else:
                return follow

        except:
            # If there is an error, return False to continue with another user
            return follow

    def select(self, cursor, table):
        """Gets the usernames that we are already following from the
        database.

        Parameters
        ----------
        cursor : Database cursor
        table : str
            Name of the table where is the data

        returns
        -------
        following : set
            set with the usernames.
        """
        if table == "User":
            cursor.execute(
                f"SELECT username FROM {table} WHERE username = '{self.username}'")
            following = cursor.fetchone()
        else:
            cursor.execute(
                f"SELECT username FROM {table} WHERE followed_by = '{self.username}'")

            if cursor.fetchall() == None:
                following = set()
                return following
            else:
                following = {row[0] for row in cursor.fetchall()}
                return following

    def insert(self, cursor, table, *args):
        """Insert data into the database

        Parameters
        ----------
        cursor : Database cursor

        table : str
            Name of the table where is the data
        """
        if table == "User":
            columns = "(username)"
            values = "(?)"
        elif table == "Following":
            columns = "(username, follower)"
            values = "(?, ?)"
        elif table == "Visited":
            columns = "(username, photos_liked, followed_by)"
            values = "(?, ?, ?)"
        elif table == "Photos":
            columns = "(link, liked_by)"
            values = "(?, ?)"

        query = f"INSERT INTO {table} {columns} values {values};"
        cursor.execute(query, tuple(args))

# if __name__ == "__main__":
#     pass
