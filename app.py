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


def keyboardinterrupt(
    instagram: Instagram, utils: Utils, users: set, filename: str
) -> None:
    print("Program interrupted...")
    print(f"{len(users)} Users pending for next session")
    pending = dict()
    pending[instagram.username] = users
    utils.save_file(pending, filename)
    sys.exit()


def close(instagram):
    conn.commit()
    conn.close()
    instagram.close()

    sys.exit()


def unfollow(instagram: Instagram, utils: Utils, users: set) -> None:
    for i in range(len(users)):
        user = users.pop()
        link = instagram.create_link(user)
        instagram.unfollow(link)
        seconds = random.randint(15, 30)
        time.sleep(seconds)
        if (i + 1) % 10 == 0:
            print(f"You have unfollowed {i+1} accounts")


def get_users_left(instagram: Instagram, utils: Utils, filename: str) -> dict:
    users_left = utils.load_file(filename)
    if instagram.username not in users_left.keys():
        users_left[instagram.username] = set()
    users_left = users_left[instagram.username]

    return users_left


def new_session(instagram: Instagram, utils: Utils) -> set:

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

    return users_left


def get_user_data():
    username = input("Enter your username: ")
    password = getpass("Enter your password, it will be deleted after login: ")

    return username, password


def new_account(instagram: Instagram, utils: Utils) -> bool:
    if instagram.username in utils.select_users():
        return False
    else:
        return True


def save_true_followers(
    instagram: Instagram, utils: Utils, followers: set, followees: set
) -> None:
    true_follower = followees.intersection(followers)
    for user in true_follower:
        utils.insert_followed_or_visited_account("Following", user, instagram.username)
    conn.commit()


def check_pending_tasks(
    instagram: Instagram, utils: Utils, unfollow_left: set, users_left: set
) -> set:

    # 1. unfollow
    if len(unfollow_left) > 1:
        print(f"There are {len(unfollow_left)} users to unfollow")
        unfollow(instagram, utils, unfollow_left)

    # 2. continue with the users or start a new session
    if len(users_left) > 1:
        n_users = len(users_left)
        print(f"There are {n_users} profiles to check")

        return users_left
    else:
        return None


def like_comment_photos(
    instagram: Instagram, utils: Utils, photos: list, user: str, comment: bool = True
) -> None:
    liked = 0
    if photos:
        for photo in photos:
            instagram.like_photo(photo)
            liked += 1
            utils.insert_photos(photo, instagram.username)
            time.sleep(3)
            comment_true = random.randint(1, 4)

            if comment and (comment_true == 1):
                instagram.comment(config.COMMENTS)
                seconds = random.randint(3, 10)
                time.sleep(seconds)

        utils.insert_followed_or_visited_account(
            "Visited", user, instagram.username, liked
        )
        conn.commit()
    else:
        print(f'The profile {user} is private or does not have photos"')
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
        print(f"{len(unfollow_left)} accounts of {len(followees)} to unfollow")
        unfollow(instagram, utils, unfollow_left)

        # Needed for next step
        users_left = set()

    else:
        print("User already in the database")
        print("Looking if there are tasks pending...")

        users_left = get_users_left(instagram, utils, config.USERS_LEFT_PATH)
        unfollow_left = get_users_left(instagram, utils, config.UNFOLLOW_LEFT_PATH)

    users_left = check_pending_tasks(instagram, utils, unfollow_left, users_left)

    if not users_left:
        users_left = new_session(instagram, utils)

    try:
        for i in range(len(users_left)):
            user = users_left.pop()
            link = instagram.create_link(user)

            need_follow = instagram.already_follow(link)

            if need_follow and config.FOLLOW:
                instagram.follow(link)
                seconds = random.randint(45, 90)
                time.sleep(seconds)

            if need_follow and config.LIKE_PHOTOS:
                photos = instagram.get_photos(link)
                like_comment_photos(
                    instagram, utils, photos, user, config.COMMENT_PHOTOS
                )

            else:
                print(f"You already follow {user}")
                continue

    except KeyboardInterrupt:
        keyboardinterrupt(instagram, utils, users_left, config.USERS_LEFT_PATH)

    except:
        keyboardinterrupt(instagram, utils, users_left, config.USERS_LEFT_PATH)

    finally:
        # Always close the database
        close(instagram)
