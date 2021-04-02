from selenium.webdriver.common.keys import Keys
from selenium import webdriver

import time
import random
import instaloader


class Instagram:
    instagram_link = "https://www.instagram.com/"

    def __init__(self, username, password, driver):
        self.username = username
        self.driver = driver
        self.password = password

        # Login to instaloader
        self.L = instaloader.Instaloader()
        self.L.login(self.username, self.password)

        # delete password
        del password
        del self.password

    def create_link(self, username):
        """
        It takes the username of an instagram account and creates a
        link to the homepage of that username
        """
        if "@" in username:
            username = username.replace('@', '')
        link = self.instagram_link + username + '/'

        return link

    def login(self, password):
        """The login function allows us to log in an instagram account."""

        # Load the login page
        self.driver.get(self.instagram_link + "accounts/login/")

        # Fill the format with username and password
        username = self.driver.find_element_by_name("username")
        username.clear()
        username.send_keys(self.username)
        passw = self.driver.find_element_by_name("password")
        passw.clear()
        passw.send_keys(password)
        passw.send_keys(Keys.RETURN)

    def get_followers(self, username, number_of_accounts=None):
        """
        Gets all the accounts that are following `username` and
        returns the `number_of_accounts` specified

        Parameters
        ----------
        username : str
        number_of_accounts : int
            Amount of followers to return. If None, 
            it returns all

        Returns
        -------
            A set with the usernames to follow 
        """
        # Get profile metadata of the user
        self.metadata = instaloader.Profile.from_username(self.L.context, username)

        # get accounts
        accounts = set()
        for i, users in enumerate(self.metadata.get_followers()):
            accounts.add(users.username)
            if number_of_accounts == None:
                continue
            else:
                if i == number_of_accounts:
                    break

        return accounts

    def get_followees(self, username):
        """
        Gets the accounts that the username is following

        Returns
        -------
            A set with the usernames that the user is following 
        """
        # Get profile metadata of the user
        self.metadata = instaloader.Profile.from_username(self.L.context, username)

        # get accounts
        accounts = set()
        for users in self.metadata.get_followees():
            accounts.add(users.username)

        return accounts

    def get_photos(self, link):
        """
        Returns a random amount of links with the photos of the `link` that we are searching

        Parameters
        ----------
        link : str
            The homepage of the instagram account from where we want to get the photos

        Returns
        -------
            List with the profile photos to like or None when the profile doesn't have photos or it is private
        """
        # self.driver.get(link)

        time.sleep(2)

        # Scroll down the page to obtain more photos
        for i in range(1, 3):
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)

        # Wait after scroll down in the profile
        time.sleep(random.randint(1, 4))

        # We add a try and except in case that the profile is private in that case we are gonna return None
        try:

            photos = []
            count = 1

            for photo in self.driver.find_elements_by_tag_name("a"):
                p = photo.get_attribute("href")

                # If the link is a photo we add it to photos. A maximum of 10
                if p.startswith("https://www.instagram.com/p/") and count <= 10:
                    photos.append(p)
                    count += 1

            # From the photos that we collect, we choose randomly which one to like
            likes = random.randint(2, 4)

            if len(photos) == 0:
                return None

            # If the profile has less photos than the number of likes, likes become the len of the list
            # Shuffle the list to return the photos in a random order
            if likes > len(photos):
                likes = len(photos)
                random.shuffle(photos)
                photos_to_like = photos[0:likes]

                return photos_to_like
            else:
                random.shuffle(photos)
                photos_to_like = photos[0:likes]

                return photos_to_like

        except:
            # If an error we assume is private or does not exists
            username = link.split("/")[-2]
            print(
                f"The account {username} is private, does not have photos or does not exists")
            return None

    def like_photo(self, link):
        """
        Gives a like to one photo.

            Parameters
            ----------
            link : str
                The link of the photo
        """

        self.driver.get(link)
        time.sleep(1)

        try:
            self.driver.find_element_by_css_selector(
                ".fr66n > button:nth-child(1)").click()
        except Exception as e:
            print("error in like function")
            print(e)

    def follow(self, link):
        """
        Follows the given user

            Parameters
            ----------
            link : str
                Homepage of the user 
        """

        time.sleep(1)
        #self.driver.get(link)
        # We move to the top of the page
        Keys.HOME
        try:
            Keys.HOME
            time.sleep(2)
            follow_button = self.driver.find_element_by_xpath(
                "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button")
            # follow_button = self.driver.find_elements_by_css_selector("._6VtSN")
            follow_button.click()
            time.sleep(1)
        except Exception as e:
            print(e)
        else:
            user = link.split('/')[-2]
            print("You followed {}".format(user))

    def unfollow(self, link):
        """
        Unfollows the given user

            Parameters
            ----------
            username : str
                The username of the instagram account

            Returns
            -------
            A string specifying which account was unfollowed 
        """

        self.driver.get(link)
        time.sleep(2)

        follow_button = self.driver.find_element_by_css_selector(".glyphsSpriteFriend_Follow")
        #follow_button = self.driver.find_element_by_class_name('_5f5mN    -fzfL     _6VtSN     yZn4P   ')
        #follow_button = self.driver.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button")
        follow_button.click()
        time.sleep(1)
        confirmation_button = self.driver.find_element_by_xpath(
            '/html/body/div[5]/div/div/div/div[3]/button[1]'
        )
        confirmation_button.click()

        return print(f"You unfollowed: {link.split('/')[-2]}")

    def comment(self, comment_list):
        """
        Choose a comment from a given list to comment a photo that you liked.

        Parameters
        ----------
        comment_list : list
            List with the possible comments 
        """
        comment = True
        try:
            enter_key = u'\ue007'
            # get the comment field and click
            comment_field = self.driver.find_element_by_class_name(
                "Ypffh").click()
            # self.driver.execute_script(
            #    'window.scrollTo(0, document.body.scrollHeight)')
        except:
            print("The comments are disabled")
            comment = False
        
        if comment:
            # If we can click on the text box, check if we can add the comment
            try:
                seconds = random.randint(1, 3)
                time.sleep(seconds)

                # From the list of comments get one
                comment_text = random.choice(comment_list)

                # We have to search for the field again to add the comment, then enter
                comment_field = self.driver.find_element_by_css_selector(".Ypffh")
                comment_field.send_keys(comment_text + enter_key)

                time.sleep(random.randint(1, 3))
            except Exception as e:
                print('Error adding the comment')
                print(e)

                

    def already_follow(self, link):
        """
        Checks if we can or cannot follow the account

        Parameters
        ----------
        username : str
            The homepage link of the account

        Returns
        -------
        follow : boolean 
        """

        self.driver.get(link)
        time.sleep(2)
        follow = False

        # We identify the follow button and then we decide what to do
        try:
            follow_button = self.driver.find_element_by_css_selector(".BY3EC")
            # Check for "Seguir" or "Follow". Depends on the user language
            if follow_button.text == "Seguir" or follow_button.text == "Follow":
                follow = True
                return follow
            else:
                return follow

        except:
            # If there is an error, return False to continue with another user
            return follow

    def close(self):
        """close the driver connection"""
        self.driver.close()


if __name__ == "__main__":
    pass