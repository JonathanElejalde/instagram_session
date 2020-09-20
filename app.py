from user import User
from getpass import getpass

import time
import random
import sqlite3
import os

# Create database if it does not exist
database_path = 'instagram.db'
if not os.path.exists(database_path):
    print("Creating database ...")
    os.system('database.py')


conn = sqlite3.connect('instagram.db')
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
if os.path.exists('credentials.py'):
    import credentials
    username = credentials.username
    password = credentials.password
else:
    username = input("Enter your username: ")
    password = getpass("Enter your password, it will be deleted after login: ")

# Create an User instance ang login
my_instagram = User(username)
# link = my_instagram.create_link(username)
my_instagram.login(password)

# Wait until it logs in
time.sleep(5)

# Delete password
del password

# Add username to the database if it is not already there
if my_instagram.select(cursor, "User") == None:
    print("User already in the database")
else:
    my_instagram.insert(cursor, "User", username)
    conn.commit()

# Get users left, it could be empty
users_left = my_instagram.load_users()

# Continue with the users or start a new session
if len(users_left) > 1:
    n_users = len(users_left)
    print(f"{n_users} profiles to check")
else:

    # We ask for the profile and the amount of users that the app will get
    new_user = input(
        "Write the username from where you want to get the followers: "
    )
    # IF THE USER STARTS WITH @ CONTINUE OTHERWISE ADD IT
    amount = input("Write the amount of followers (the maximum is 2000): ")
    amount = int(amount)

    # Get the users that we are following
    following = my_instagram.select(cursor, "Following")

    # Get the visited users
    visited = my_instagram.select(cursor, "Visited")

    # Create a union with following and visited
    union = following.union(visited)

    # Get the users from the new_user
    link = my_instagram.create_link(new_user)
    users_left = my_instagram.get_profiles(link, amount, following)

    # The users left will be the difference between the two sets
    users_left = list(users_left.difference(union))

# Now we iterate over every user left in the resulting set.
try:
    for i, user in enumerate(users_left):
        link = my_instagram.create_link(user)

        # Check if we are already following the account
        follow = my_instagram.already_follow(link)

        if follow == False:
            continue

        # Get the photos
        photos = my_instagram.get_photos(link)

        if photos == None:
            print(f'The profile {user} is private or does not have photos"')
            my_instagram.insert(cursor, "Visited", user, 0, username)
            continue

        # Follow and then like and comment the photos
        my_instagram.follow(link)
        # Wait
        seconds = random.randint(45, 90)
        time.sleep(seconds)

        # Like the photos and 25% chance of comment the photo
        for photo in photos:
            try:
                my_instagram.like_photo(photo)
                liked = 1

                # comment?
                comment = random.randint(1, 4)
                if comment == 1:
                    my_instagram.comment(comments)
                    seconds = random.randint(3, 10)
                    time.sleep(seconds)
                else:
                    comment = 0

                # Wait for like the next photo
                seconds = random.randint(3, 10)

                # Add to database
                my_instagram.insert(cursor, "Photos", photo, username)
                conn.commit()
            except:
                print("Could not like or comment the photo in {user}")
                continue

        # Add this user to the Visited table in the database
        # Before continue with other user
        my_instagram.insert(cursor, "Visited", user, len(photos), username)
        conn.commit()

except KeyboardInterrupt:
    print("Program interrupted...")

except Exception as e:
    print("An special error has occurred")
    print(e)
finally:
    # Always close the database, the driver and save the users_left
    conn.close()
    my_instagram.close()
    my_instagram.save_users(users_left[i:])
