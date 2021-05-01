from getpass import getpass
from selenium import webdriver
from utils import Utils
from instagram import Instagram

import config
import time
import random
import sqlite3
import os
import sys


def save_users_left(
    instagram: Instagram, utils: Utils, users: dict, filename: str
) -> None:
    """
    Saves the users that the current session did not visite.
    """
    print("Closing program...")
    if len(users) < 1:
        print("Not users left")
    else:
        print(f"{len(users[instagram.username])} Users pending for next session")
    utils.save_file(users, filename)
    sys.exit()


def close(instagram):
    """
    Commits latest changes, and closes database and selenium webdriver
    connections.
    """
    conn.commit()
    conn.close()
    instagram.close()

    sys.exit()


def unfollow(instagram: Instagram, utils: Utils, pending_unfollows: set) -> None:
    """Takes a dict of users and gets the accounts to unfollow using selenium webdriver"""

    unfollow_left = pending_unfollows[instagram.username]
    for i in range(len(unfollow_left)):
        user = unfollow_left.pop()
        try:
            link = instagram.create_link(user)
            instagram.unfollow(link)
            seconds = random.randint(15, 30)
            time.sleep(seconds)
        except KeyboardInterrupt:
            pending_unfollows[instagram.username] = unfollow_left
            save_users_left(
                instagram, utils, pending_unfollows, config.UNFOLLOW_LEFT_PATH
            )
            close(instagram)

        except Exception as e:
            print(f"Following error appear when visiting {user}:\n{e}")
            seconds = random.randint(5, 10)
            time.sleep(seconds)
            continue

        if (i + 1) % 10 == 0:
            print(f"You have unfollowed {i+1} accounts")


def get_users_left(instagram: Instagram, utils: Utils, filename: str) -> dict:
    """Loads a dict and returns the accounts left"""
    pending_tasks = utils.load_file(filename, instagram.username)
    if instagram.username not in pending_tasks.keys():
        pending_tasks[instagram.username] = set()

    return pending_tasks


def new_session(instagram: Instagram, utils: Utils) -> set:
    """Asks for an instagram account and number of followers. Then, visits
    the account and return the amount of followers in a set.

    Note: It avoids accounts that we already follow"""

    new_user = input("Write the username from where you want to get the followers: ")
    amount = input("Write the amount of followers to get: ")
    amount = int(amount)

    following = utils.select_followees("Following", instagram.username)
    visited = utils.select_followees("Visited", instagram.username)

    union = following.union(visited)

    print("Getting new accounts, please wait...")
    users_left = instagram.get_followers(new_user, amount)
    users_left = users_left.difference(union)

    print(f"{len(users_left)} to check")

    pending_users_left = dict()
    pending_users_left[instagram.username] = users_left

    return pending_users_left


def get_user_data():
    """Asks login data to the user"""
    username = input("Enter your username: ")
    password = getpass("Enter your password, it will be deleted after login: ")

    return username, password


def new_account(instagram: Instagram, utils: Utils) -> bool:
    """Returns True if we are using a new account, else False"""
    if instagram.username in utils.select_users():
        return False
    else:
        return True


def save_true_followers(
    instagram: Instagram, utils: Utils, followers: set, followees: set
) -> None:
    """Inserts true followers accounts to a database. True followers are the ones
    that we follow and they follow us back"""
    true_follower = followees.intersection(followers)
    for user in true_follower:
        utils.insert_followed_or_visited_account("Following", user, instagram.username)
    conn.commit()


def check_pending_tasks(
    instagram: Instagram, utils: Utils, pending_unfollows: dict, pending_users_left: set
) -> set:

    # Get pending tasks for this current user
    unfollow_left = pending_unfollows[instagram.username]
    users_left = pending_users_left[instagram.username]

    # 1. unfollow
    if len(unfollow_left) > 1:
        print(f"There are {len(unfollow_left)} users to unfollow")
        unfollow(instagram, utils, pending_unfollows)

    # 2. continue with the users or start a new session
    if len(users_left) > 1:
        n_users = len(users_left)
        print(f"There are {n_users} profiles to check")

        return pending_users_left
    else:
        return None


def like_comment_photos(
    instagram: Instagram, utils: Utils, photos: list, user: str, comment: bool = True
) -> None:
    liked = 0
    commented = 0
    if photos:
        for photo in photos:
            instagram.like_photo(photo)
            liked += 1
            utils.insert_photos(photo, instagram.username)
            time.sleep(3)
            comment_true = random.randint(1, 4)

            if comment and (comment_true == 1):
                instagram.comment(config.COMMENTS, photo)
                seconds = random.randint(3, 10)
                time.sleep(seconds)
                commented += 1

        utils.insert_followed_or_visited_account(
            "Visited", user, instagram.username, liked
        )
        conn.commit()
        print(f"You commented {commented} and liked {liked} photos on {user}")
    else:
        utils.insert_followed_or_visited_account("Visited", user, instagram.username, 0)


if __name__ == "__main__":
    driver = webdriver.Firefox(executable_path="geckodriver/geckodriver")
    driver.implicitly_wait(20)

    if not os.path.exists(config.DATABASE_PATH):
        print("Creating database ...")
        os.system("python3 database.py")

    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()

    username, password = get_user_data()

    # Login
    utils = Utils(cursor)
    instagram = Instagram(username, password, driver)

    # Wait for login
    time.sleep(3)
    print("Login done")

    del password

    if new_account(instagram, utils):
        utils.insert_user(username)
        print("Getting accounts, please wait...")

        followers = instagram.get_followers(username)
        followees = instagram.get_followees(username)

        save_true_followers(instagram, utils, followers, followees)

        # Unfollow accounts that don't follow back
        unfollow_left = followees.difference(followers)
        pending_unfollows = dict()
        pending_unfollows[instagram.username] = unfollow_left

        print(f"{len(unfollow_left)} accounts of {len(followees)} to unfollow")
        unfollow(instagram, utils, pending_unfollows)

        # Needed for next step
        pending_unfollows[instagram.username] = set()
        pending_users_left = dict()
        pending_users_left[instagram.username] = set()

    else:
        print("User already in the database")
        print("Looking if there are tasks pending...")

        pending_users_left = get_users_left(instagram, utils, config.USERS_LEFT_PATH)
        pending_unfollows = get_users_left(instagram, utils, config.UNFOLLOW_LEFT_PATH)

    pending_users_left = check_pending_tasks(
        instagram, utils, pending_unfollows, pending_users_left
    )

    if not pending_users_left:
        pending_users_left = new_session(instagram, utils)

    # Get users left for current session
    users_left = pending_users_left[instagram.username]

    for i in range(len(users_left)):
        user = users_left.pop()
        link = instagram.create_link(user)

        need_follow = instagram.already_follow(link)

        try:
            if need_follow and config.LIKE_PHOTOS:
                photos = instagram.get_photos(link)
                like_comment_photos(
                    instagram, utils, photos, user, config.COMMENT_PHOTOS
                )

                if photos and config.FOLLOW:
                    instagram.follow(link)
                    seconds = random.randint(45, 90)
                    time.sleep(seconds)

            else:
                print(f"You already follow {user}")
                seconds = random.randint(5, 15)
                time.sleep(seconds)
                continue

        except KeyboardInterrupt:
            pending_users_left[instagram.username] = users_left
            save_users_left(
                instagram, utils, pending_users_left, config.USERS_LEFT_PATH
            )
            close(instagram)

        except Exception as e:
            print(f"Following error appear when visiting {user}:\n{e}")
            seconds = random.randint(5, 15)
            time.sleep(seconds)
            continue

    # If not users left, save empty set and close
    pending_users_left[instagram.username] = users_left
    save_users_left(instagram, utils, pending_users_left, config.USERS_LEFT_PATH)
    close(instagram)
