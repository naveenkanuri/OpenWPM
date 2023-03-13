""" This file aims to demonstrate how to write custom commands in OpenWPM

Steps to have a custom command run as part of a CommandSequence

1. Create a class that derives from BaseCommand
2. Implement the execute method
3. Append it to the CommandSequence
4. Execute the CommandSequence

"""
import logging
import time

from selenium.webdriver import Firefox

from openwpm.commands.types import BaseCommand
from openwpm.commands.utils.webdriver_utils import scroll_down
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket


class CookieAnalyzerCommand(BaseCommand):
    """This command logs how many links it found on any given page"""

    def __init__(self) -> None:
        self.logger = logging.getLogger("openwpm")

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "CookieAnalyzerCommand"

    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        cookies = webdriver.get_cookies()
        print(f'cookieCount = {len(cookies)}')
        # print the cookie details to the console
        # print the cookie details to the console
        for cookie in cookies:
            print("Cookie Name:", cookie['name'])
            print("Cookie Value:", cookie['value'])
            print("Domain:", cookie['domain'])
            print("Path:", cookie['path'])
            print("Expiry:", cookie['expiry'])
            print("Is HttpOnly:", cookie['httpOnly'])
            print("Is Secure:", cookie['secure'])
            print("SameSite:", cookie['sameSite'])
            print("Size:", len(cookie))
            print("----------------------------------------")

        # print('scrolling?')
        scroll_down(webdriver)
        # wait for 5 seconds
        # time.sleep(5)

        # get all the cookies again
        updated_cookies = webdriver.get_cookies()

        # compare the cookies to detect any changes
        for updated_cookie in updated_cookies:
            for cookie in cookies:
                if updated_cookie['name'] == cookie['name']:
                    if updated_cookie['value'] != cookie['value']:
                        print("Cookie Value Changed:", cookie['name'])
                    if updated_cookie['path'] != cookie['path']:
                        print("Cookie Path Changed:", cookie['name'])
                    if updated_cookie['expiry'] != cookie['expiry']:
                        print("Cookie Expiry Changed:", cookie['name'])
                    if updated_cookie['httpOnly'] != cookie['httpOnly']:
                        print("Cookie HttpOnly Changed:", cookie['name'])
                    if updated_cookie['secure'] != cookie['secure']:
                        print("Cookie Secure Changed:", cookie['name'])
                    if updated_cookie['sameSite'] != cookie['sameSite']:
                        print("Cookie SameSite Changed:", cookie['name'])
                    if len(updated_cookie) != len(cookie):
                        print("Cookie Size Changed:", cookie['name'])
                    break
            else:
                print("New Cookie Added:", updated_cookie['name'])
