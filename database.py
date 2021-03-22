import sqlite3

"""
User: This contains the instagram accounts that use the app
Following: This are the users that the instagram account is currently following.
    username: is the account followed
    followed_by: One of the accounts using the program
Visited: To know what we did in the profile we visited
    username: the account visited
    photos_liked: amount of photos that we gave a like
    followed_by: the account that followed the username
    unfollow: in case that the account in followed_by decides to unfollow username (will be 1, null otherwise)
Photos: Photos with a like
    link: photo's link
    liked_by: the account that gave the like
"""

conn = sqlite3.connect('instagram.db')
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")
cur.executescript(
"""
CREATE TABLE IF NOT EXISTS User(
	username TEXT NOT NULL UNIQUE PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Following(
    username TEXT NOT NULL,
    followed_by TEXT NOT NULL,
    FOREIGN KEY (followed_by) REFERENCES User (username)
);

CREATE TABLE IF NOT EXISTS Visited(
    username TEXT NOT NULL,
    photos_liked INTEGER,
    followed_by TEXT NOT NULL,
    unfollow INTEGER DEFAULT NULL,
    FOREIGN KEY (followed_by) REFERENCES User (username)
);

CREATE TABLE IF NOT EXISTS Photos(
    link TEXT NOT NULL,
    liked_by TEXT NOT NULL,
    FOREIGN KEY (liked_by) REFERENCES User (username)
);
""")

conn.commit()


if __name__ == "__main__":
    pass
