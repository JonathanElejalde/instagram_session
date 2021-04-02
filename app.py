from user import User
from getpass import getpass
from selenium import webdriver

import time
import random
import sqlite3
import os
import sys

def keyboardinterrupt(my_instagram, users, filename):
    print("Program interrupted...")
    print(f'{len(users)} Users pending for next session')
    pending = dict()
    pending[my_instagram.username] = users
    my_instagram.save_users(pending, filename)

    sys.exit()

def other_exception(error, my_instagram, users, filename):
    print("An special error has occurred")
    print(error)

    print(f'\n{len(users)} Users pending for next session')
    pending = dict()
    pending[my_instagram.username] = users
    my_instagram.save_users(pending, filename)

    sys.exit()

def close(my_instagram):
    conn.commit()
    conn.close()
    my_instagram.close()

    sys.exit()

def unfollow(my_instagram, users):

    try:
        total = len(users)
        for i in range(total):
            user = users.pop()
            link = my_instagram.create_link(user)
            my_instagram.unfollow(link)
            if (i+1) % 10 == 0:
                print(f'{i + 1} users of {total} unfollowed')
            # Wait
            seconds = random.randint(15, 30)
            time.sleep(seconds)
    except KeyboardInterrupt:
        keyboardinterrupt(my_instagram, users, UNFOLLOW_LEFT_PATH)
        
    except Exception as e:
        other_exception(e, my_instagram, users, UNFOLLOW_LEFT_PATH)

def get_users_left(my_instagram, filename):
    users_left = my_instagram.load_users(filename)
    if my_instagram.username not in users_left.keys():
        users_left[my_instagram.username] = set()
    users_left = users_left[my_instagram.username]

    return users_left

def new_session(my_instagram):
    # We ask for the profile and the amount of users that the app will get
    new_user = input(
        "Write the username from where you want to get the followers: "
    )
    amount = input("Write the amount of followers to get: ")
    amount = int(amount)

    # Get the users that we are following
    following = my_instagram.select(cursor, "Following")

    # Get the visited users
    visited = my_instagram.select(cursor, "Visited")

    # Create a union with following and visited
    union = following.union(visited)

    # Get the users from the new_user
    print('Getting accounts, please wait...')
    users_left = my_instagram.get_followers(new_user, amount)

    # The users left will be the difference between the two sets
    users_left = users_left.difference(union)

    print(f'{len(users_left)} to check')

    return users_left

# Variables
USERS_LEFT_PATH = 'users_left.data'
UNFOLLOW_LEFT_PATH = 'unfollow_left.data'
FOLLOW = True

# Initialize the driver
driver = webdriver.Firefox(executable_path="geckodriver/geckodriver")

# Wait maximum 10 seconds for the elements in the page
driver.implicitly_wait(20)

# Create database if it does not exist
database_path = './instagram.db'
if not os.path.exists(database_path):
    print("Creating database ...")
    os.system('python3 database.py')


conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# Comment's list
comments = [
    "Great!" + " \U0001F60E",
    "Nice!" + " \U0001F60E",
    "Genial" + " \U0001F60E",
    "\U0001F601",
    "\U0001F604",
    "\U0001F600",
    "\U0001F60E",
]

# Login the account
# Alternative login with credentials file
username = input("Enter your username: ")
password = getpass("Enter your password, it will be deleted after login: ")

# Create an User instance ang login
my_instagram = User(username, password, driver)
my_instagram.login(password)
print('Login done')

# Wait for login
time.sleep(3)

# Delete password
del password

# Add username to the database if it is not already there
if username in my_instagram.select(cursor, "User"):
    print("User already in the database")
    print('Looking if there are tasks pending...')

    # Load users_left and unfollow_left for this user if they exist
    users_left = get_users_left(my_instagram, USERS_LEFT_PATH)
    unfollow_left = get_users_left(my_instagram, UNFOLLOW_LEFT_PATH)
else:
    my_instagram.insert(cursor, "User", username)
    print('Getting accounts, please wait...')
    # If the account not in database, unfollow accounts
    # that are not following back
    followers = my_instagram.get_followers(username)
    followees = my_instagram.get_followees(username)

    # Save accounts that you follow and follow you back
    users2save = followees.intersection(followers)
    for user in users2save:
        my_instagram.insert(cursor, 'Following', user, my_instagram.username)
    conn.commit()

    # Unfollow accounts that don't follow back
    unfollow_left = followees.difference(followers)
    print(f'{len(unfollow_left)} accounts of {len(followees)} to unfollow')
    unfollow(my_instagram, unfollow_left)

    # Set users_left to an empty set. Needed for next step
    users_left = set()

# CHECK PENDING TASKS

# 1. unfollow
if len(unfollow_left) > 1:
    print(f'There are {len(unfollow_left)} users to unfollow')
    unfollow(my_instagram, unfollow_left)

# 2. continue with the users or start a new session
if len(users_left) > 1:
    n_users = len(users_left)
    print(f"There are {n_users} profiles to check")
else:
    users_left = new_session(my_instagram)

# Now we iterate over every `user_left`

try:
    for i in range(len(users_left)):
        user = users_left.pop()
        link = my_instagram.create_link(user)

        # Check if we are already following the account
        follow = my_instagram.already_follow(link)

        if follow == False:
            print(f'You already follow {user}')
            continue

        # Get the photos
        photos = my_instagram.get_photos(link)

        if photos == None:
            print(f'The profile {user} is private or does not have photos"')
            my_instagram.insert(cursor, "Visited", user, 0, username)
            continue

        # Follow and then like and comment the photos
        if FOLLOW:
            my_instagram.follow(link)
            # Wait
            seconds = random.randint(45, 90)
            time.sleep(seconds)

        # Like the photos and 25% chance of comment the photo
        for photo in photos:
            my_instagram.like_photo(photo)
            liked = 1

            # comment?
            comment = random.randint(1, 4)
            comments = 0
            if comment == 1:
                my_instagram.comment(comments)
                comments += 1
                seconds = random.randint(3, 10)
                time.sleep(seconds)
            else:
                comment = 0

            # Wait for like the next photo
            seconds = random.randint(3, 10)

            # Add to database
            my_instagram.insert(cursor, "Photos", photo, username)
            conn.commit()

        # Show recap
        print(f"You liked {len(photos)} photos and commented {comments} on {user}'s profile")

        # Add this user to the Visited table in the database
        # Before continue with another user
        my_instagram.insert(cursor, "Visited", user, len(photos), username)
        conn.commit()

except KeyboardInterrupt:
        keyboardinterrupt(my_instagram, users_left, USERS_LEFT_PATH)
        
except Exception as e:
    other_exception(e, my_instagram, users_left, USERS_LEFT_PATH)
        
finally:
    # Always close the database, the driver and save the users_left
    close(my_instagram)
