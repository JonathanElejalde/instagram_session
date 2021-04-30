from selenium.webdriver.common.keys import Keys
from selenium import webdriver

import time
import random
import instaloader


class Instagram:
    """Class for handling instagram functionalities"""

    instagram_link = "https://www.instagram.com/"

    def __init__(self, username: str, password: str, driver: webdriver) -> None:
        self.username = username
        self.driver = driver
        self.password = password

        # Login to instaloader
        self.profile = self._login_instaloader()

        # Login to instagram
        self._login_instagram()

        # delete password
        del password
        del self.password

    def _login_instaloader(self):
        profile = instaloader.Instaloader()
        profile.login(self.username, self.password)

        return profile

    def _get_instaloader_metadata(self, username):
        metadata = instaloader.Profile.from_username(self.profile.context, username)

        return metadata

    def _check_current_url(self, link: str) -> bool:
        """Checks if current link is the same as the required
        link"""

        return self.driver.current_url == link

    def create_link(self, username: str) -> str:
        """
        Creates a instagram homepage link with `username`
        """
        if "@" in username:
            username = username.replace("@", "")
        link = self.instagram_link + username + "/"

        return link

    def _get_username(self, link: str) -> str:
        username = link.split("/")[-2]
        return username

    def _login_instagram(self) -> None:
        """Login an instagram account with selenium"""

        # Login page
        self.driver.get(self.instagram_link + "accounts/login/")

        # Fill login format
        username = self.driver.find_element_by_name("username")
        username.clear()
        username.send_keys(self.username)
        passw = self.driver.find_element_by_name("password")
        passw.clear()
        passw.send_keys(self.password)
        passw.send_keys(Keys.RETURN)

        time.sleep(5)

    def get_followers(self, username: str, number_of_accounts: int = None) -> set:
        """
        Gets all the accounts that are following `username` and
        returns the specified `number_of_accounts`
        """
        metadata = self._get_instaloader_metadata(username)

        accounts = set()
        for i, users in enumerate(metadata.get_followers()):
            accounts.add(users.username)
            if i == number_of_accounts:
                break

        return accounts

    def get_followees(self, username: str) -> set:
        """
        Gets the accounts that `username` is following
        """
        metadata = self._get_instaloader_metadata(username)

        # get accounts
        accounts = set()
        for users in metadata.get_followees():
            accounts.add(users.username)

        return accounts

    def get_photos(self, link: str) -> list:
        """
        Returns a random amount of instagram photo from the current link or None
        if there are not photos or the account is private
        """

        if not self._check_current_url(link):
            self.driver.get(link)
            time.sleep(2)

        # Scroll down the page to obtain more photos
        for i in range(1, 3):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)

        time.sleep(random.randint(1, 3))

        try:

            photos = []
            count = 1

            for photo in self.driver.find_elements_by_tag_name("a"):
                p = photo.get_attribute("href")

                # Checks photos. Maximum 10
                if p.startswith("https://www.instagram.com/p/") and count <= 10:
                    photos.append(p)
                    count += 1

            # Amount of photos we will return
            likes = random.randint(2, 4)

            # Private or empty account
            if len(photos) == 0:
                username = self._get_username(link)
                print(f"The account {username} is private or empty")
                return None

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
            username = self._get_username(link)
            print(f"The account {username} is private, empty or does not exist")
            return None

    def like_photo(self, link: str) -> str:
        """
        Likes an instagram photo
        """

        if not self._check_current_url(link):
            self.driver.get(link)
            time.sleep(2)

        try:
            self.driver.find_element_by_css_selector(
                ".fr66n > button:nth-child(1)"
            ).click()
        except Exception as e:
            print("error in like function")
            print(e)

    def follow(self, link: str) -> None:
        """
        Follows the given user
        """

        if not self._check_current_url(link):
            self.driver.get(link)
            time.sleep(2)

        # We move to the top of the page
        Keys.HOME
        try:
            Keys.HOME
            time.sleep(2)
            element = "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button"
            follow_button = self.driver.find_element_by_xpath(element)
            # follow_button = self.driver.find_elements_by_css_selector("._6VtSN")
            follow_button.click()
            time.sleep(1)
        except Exception as e:
            print(e)
        else:
            user = link.split("/")[-2]
            print("You followed {}".format(user))

    def unfollow(self, link: str) -> None:
        """
        Unfollows an account
        """
        if not self._check_current_url(link):
            self.driver.get(link)
            time.sleep(2)

        element = ".glyphsSpriteFriend_Follow"
        try:
            follow_button = self.driver.find_element_by_css_selector(element)
            follow_button.click()

            time.sleep(1)

            confirmation_button = self.driver.find_element_by_xpath(
                "/html/body/div[5]/div/div/div/div[3]/button[1]"
            )
            confirmation_button.click()
            print(f"You unfollowed: {self._get_username(link)}")
        except:

            print(f"Error unfollowing {self._get_username(link)}")

    def comment(self, comment_list: list, link: str) -> None:
        """
        Choose a comment from the given list an comment on `link`
        """

        if not self._check_current_url(link):
            self.driver.get(link)
            time.sleep(2)

        disabled = False
        # Check disabled comments
        try:
            enter_key = "\ue007"

            # gets the comment field and clicks
            comment_field = self.driver.find_element_by_class_name("Ypffh").click()

            # self.driver.execute_script(
            #    'window.scrollTo(0, document.body.scrollHeight)')
        except:
            print("The comments are disabled")
            disabled = True

        if not disabled:
            try:
                seconds = random.randint(1, 3)
                time.sleep(seconds)

                # Get one comment
                comment_text = random.choice(comment_list)

                # We have to search for the field again
                comment_field = self.driver.find_element_by_css_selector(".Ypffh")
                comment_field.send_keys(comment_text + enter_key)

                time.sleep(random.randint(1, 3))
            except Exception as e:
                print("Error adding the comment")
                print(e)

    def already_follow(self, link: str) -> bool:
        """
        Checks if the current account follows the target account.
        Returns True if need to follow
        """

        if not self._check_current_url(link):
            self.driver.get(link)
            time.sleep(2)

        need_follow = False

        try:
            element = ".BY3EC"
            follow_button = self.driver.find_element_by_css_selector(element)

            # Check for "Seguir" or "Follow". Depends on the user language
            if follow_button.text == "Seguir" or follow_button.text == "Follow":
                need_follow = True
                return need_follow
            else:
                return need_follow

        except:
            # If there is an error, return False to continue with another user
            return need_follow

    def close(self):
        """close the driver connection"""
        self.driver.close()


if __name__ == "__main__":
    pass
