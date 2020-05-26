#######################################################################
#
# This files generates LinkedIn cookies using pickle
#
#  Run this file and login to your LinkedIn account
#  Once logged in, press any key to continue and the script will generate a pickle file (*.pkl)
#  Once the pickle file is generated, run scraper.py and it will auto log you in to LinkedIn
#
#######################################################################

import pickle
from selenium import webdriver
from sys import platform
import json
import colorama
from colorama import Fore, Back, Style, init
init()


def get_driver(driver_path):
    if platform == "win32":
        # windows
        driver_instance = webdriver.Chrome()
        return driver_instance
    else:
        # linux/macOS
        chrome_options = webdriver.ChromeOptions()
        # can't login if you run this in headless mode ;)
        driver_instance = webdriver.Chrome(chrome_options=chrome_options, executable_path=driver_path)
        return driver_instance


settings = {}
drive = None

try:
    with open('config.json') as f:
        settings = json.load(f)
except Exception as fe:
    print(Fore.RED + 'Error reading config.json file.')
    print(Fore.RED + str(fe))
    exit(-1)

try:
    driver = get_driver(settings["chromeDriverLocation"])
    driver.get("https://www.linkedin.com/login")
except Exception as de:
    print(Fore.RED + 'Error launching chromedriver.')
    print(Fore.RED + str(de))
    exit(-1)

# quick cross-platform way to implement the 'Press Enter to ...'
try:
    input(Fore.YELLOW + "Press ENTER to continue when you've successfully logged in to LinkedIn.com:")
except SyntaxError:
    pass

print(Fore.YELLOW + 'Generating cookies...')
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
driver.quit()
print(Fore.GREEN + f'Cookies generated successfully!')
