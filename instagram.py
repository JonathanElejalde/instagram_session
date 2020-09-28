from selenium.webdriver.common.keys import Keys

import time
import random


class Instagram:
    instagram_link = "https://www.instagram.com/"

    def __init__(self, username, driver):
        self.username = username if username.startswith(
            '@') else '@' + username
        self.driver = driver

    def create_link(self, profile):
        """It takes the profile name of an instagram account and creates a
        link to the homepage of that profile"""
        if "@" in profile:
            profile = profile.replace('@', '')
        link = self.instagram_link + profile + '/'

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

    def get_profiles(self, link, number_of_accounts, following=None):
        """The get profiles function enters to an instagram homepage and gathers an specific number of
        usernames that are following the profile

        Parameters
        ----------
        link : str
            Link of the homepage that we want to visit
        number_of_accounts : int
            Amount of followers to get
        following : set
            Set with the usernames that our account is currently following

        Returns
        -------
            A set with the usernames to follow """

        if following is None:
            following = set()

        assert type(number_of_accounts) == int, "It is not a number"

        if number_of_accounts > 2000:
            number_of_accounts = 2000
            print("The program can collect just 2000 usernames")

        self.driver.get(link)

        # Identify the followers button
        followers_button = self.driver.find_element_by_css_selector("ul li a")
        time.sleep(2)
        followers_button.click()
        time.sleep(3)

        # Look at the list, it just show the firts 12 so we store that number into number_of_followers
        followers_list = self.driver.find_element_by_css_selector(
            "div[role='dialog'] ul")
        number_of_followers = len(
            followers_list.find_elements_by_css_selector("li"))
        followers_list.click()

        # number_of_accounts is the amount of followers that we want to capture, so we scroll down the list of followers until number_of_followers matches that number

        action_chain = webdriver.ActionChains(self.driver)
        while number_of_followers <= number_of_accounts:
            action_chain.key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
            number_of_followers = len(
                followers_list.find_elements_by_css_selector("li"))
            time.sleep(2)

        # followers will keep the username of the accounts that we are not already following
        followers = set()
        for user in followers_list.find_elements_by_css_selector("li"):
            user_link = user.find_element_by_css_selector(
                "a").get_attribute("href")

            # Separate the username from the link
            name = user_link.split('/')[-2]
            print(name)

            if user_link not in following:
                followers.add(name)

        return followers

    def get_photos(self, link):
        """The get photos function returns a random amount of links with the photos
        of the profile that we are searching

        Parameters
        ----------
        link : str
            The homepage of the instagram account from where we want to get the photos

        Returns
        -------
            List with the profile photos to like or None when the profile doesn't have photos or it is private"""

        # try:
        #     if self.driver.current_url == link:
        #         pass

        #     else:
        #         self.driver.get(link)
        # except:
        #     pass

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
        """Gives a like to one photo.

            Parameters
            ----------
            link : str
                The link of the photo"""

        self.driver.get(link)
        time.sleep(1)

        try:
            self.driver.find_element_by_css_selector(
                ".fr66n > button:nth-child(1)").click()
        except Exception as e:
            print("error in like function")
            print(e)

    def follow(self, link):
        """Follows the given user

            Parameters
            ----------
            link : str
                Homepage of the user """
        # try:
        #     if self.driver.current_url == link:
        #         pass

        #     else:
        #         self.driver.get(link)
        # except:
        #     pass

        time.sleep(1)
        # We move to the top of the page
        Keys.HOME

        time.sleep(2)
        try:
            follow_button = self.driver.find_element_by_xpath(
                "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button")
            # follow_button = self.driver.find_elements_by_css_selector("._6VtSN")
            follow_button.click()
        except Exception as e:
            print(e)
        finally:
            user = link.split('/')[-2]
            print("It was not possible to follow {}".format(user))

    def unfollow(self, link):
        """Unfollows the given user

            Parameters
            ----------
            username : str
                The username of the instagram account

            Returns
            -------
            A string specifying which account was unfollowed """

        self.driver.get(link)
        time.sleep(2)

        # follow_button = self.driver.find_element_by_css_selector(".BY3EC")
        follow_button = self.driver.find_element_by_xpath(
            "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button"
        )
        follow_button.click()
        time.sleep(1)
        confirmation_button = self.driver.find_element_by_xpath(
            '/html/body/div[4]/div/div/div/div[3]/button[1]'
        )
        confirmation_button.click()

        return print(f"You unfollowed: {username}")

    def comment(self, comment_list):
        """Choose a comment from a given list to comment a photo that you liked.

        Parameters
        ----------
        comment_list : list
            List with the possible comments """

        try:
            enter_key = u'\ue007'
            # get the comment field and click
            comment_field = self.driver.find_element_by_class_name(
                "Ypffh").click()
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight)')

            # Wait # seconds after like a photo
            seconds = random.randint(1, 3)
            time.sleep(seconds)

            # From the list of comments get one
            comment_text = random.choice(comment_list)

            # We have to search for the field again to add the comment, then enter
            comment_field = self.driver.find_element_by_css_selector(".Ypffh")
            comment_field.send_keys(comment_text + enter_key)

            time.sleep(random.randint(1, 3))
        except:
            print("The comments are disabled")

    def who_i_follow(self, link):
        """Gets the accounts that the username is following

        Parameters
        ----------
        link : str
            The homepage of the account

        Returns
        -------
            A list with the account links that the user is following """

        self.driver.get(link)

        # Now we catch the amount of people that we are following to have a limit
        following_number = self.driver.find_element_by_xpath(
            "/html/body/div[1]/section/main/div/header/section/ul/li[3]/a/span"
        ).text
        if '.' in following_number:
            following_number = following_number.replace('.', '')
        following_number = int(following_number)
        # We reduce the number because it never gets all the accounts
        following_number -= 5

        # Identify the followers button and then click on it
        following_button = self.driver.find_element_by_css_selector(
            "li.Y8-fY:nth-child(3) > a:nth-child(1)"
        )
        time.sleep(2)
        following_button.click()
        time.sleep(2)

        # Look at the list, it just show the firts 12 so we store that number into number_of_followers
        followers_list = self.driver.find_element_by_css_selector(
            "div[role='dialog'] ul")
        number_of_followers = len(
            followers_list.find_elements_by_css_selector("li"))
        # print(number_of_followers)
        followers_list.click()

        action_chain = webdriver.ActionChains(self.driver)
        while number_of_followers < following_number:
            action_chain.key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
            number_of_followers = len(
                followers_list.find_elements_by_css_selector("li"))
            time.sleep(2)
            print(number_of_followers)

        following = []
        for user in followers_list.find_elements_by_css_selector("li"):
            user_link = user.find_element_by_css_selector(
                "a").get_attribute("href")
            # print(user_link)
            following.append(user_link)
            if len(following) >= following_number:
                break

        return following

    def close(self):
        """close the driver connection"""
        self.driver.close()


if __name__ == "__main__":
    pass
