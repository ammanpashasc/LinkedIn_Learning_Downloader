import os
import urllib.request
from sys import platform
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import pickle
from pathlib import Path
import json
import colorama
from colorama import Fore, Back, Style, init
import time

# On Windows, calling init() will filter ANSI escape sequences out of any text sent to stdout or stderr,
# and replace them with equivalent Win32 calls. On other platforms, calling init() has no effect
init()


#  Helper method to reset console styles using colorama
def reset_console_style():
    print(Style.RESET_ALL, end='')


#  Helper method to check if an element exists on a page
def check_element_exists_by_xpath(_driver: webdriver, _xpath):
    try:
        _driver.find_element_by_xpath(_xpath)
        return True
    except NoSuchElementException:
        return False


def get_driver(driver_path, headless=False):
    if platform == "win32":
        # windows
        driver_instance = webdriver.Chrome()
        return driver_instance
    else:
        # linux
        chrome_options = webdriver.ChromeOptions()
        if headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1280x1696')
            chrome_options.add_argument('--hide-scrollbars')
            chrome_options.add_argument('--enable-logging')
            chrome_options.add_argument('--log-level=0')
            chrome_options.add_argument('--v=99')
            chrome_options.add_argument('--single-process')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument(
                'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
        driver_instance = webdriver.Chrome(chrome_options=chrome_options, executable_path=driver_path)
        return driver_instance


# Global variables
settings = {}
driver = None
DOWNLOAD_PATH = os.path.join(os.getcwd(), 'Downloads')
folder_list = []
courses_to_download = []
# list of list; [ [course_1_title, course_1_url], [course_2_title, course_2_url], [course_N_title, course_N_url] ]


# Read config.json file
try:
    with open('config.json') as f:
        settings = json.load(f)
        for course in settings["courses"]:
            courses_to_download.append([course["title"], course["url"]])

        print(Fore.YELLOW + f'Courses to download: {len(courses_to_download)}')
except Exception as fe:
    print(Fore.RED + 'Error reading config.json file.')
    print(Fore.RED + str(fe))
    exit(-1)


# Initiate webdriver and login
try:
    driver = get_driver(settings["chromeDriverLocation"], settings["runHeadless"])
    driver.maximize_window()
    driver.get("https://www.linkedin.com/learning/")
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        if isinstance(cookie.get('expiry'), float):
            cookie['expiry'] = int(cookie['expiry'])
        driver.add_cookie(cookie)

    driver.get("https://www.linkedin.com/learning/")
except Exception as de:
    print(Fore.RED + 'Error launching chromedriver.')
    print(Fore.RED + str(de))
    exit(-1)

try:
    for course_index, course in enumerate(courses_to_download):
        try:
            folder_list = []
            waited_for_load_check = False
            print(Fore.YELLOW + f'Downloading course {course_index+1}/{len(courses_to_download)}')
            print(Style.BRIGHT + Fore.YELLOW + course[0])
            driver.get(course[1])
            section_expanders = driver.find_elements_by_xpath("//li-icon[@class='classroom-toc-chapter__toggle-state']")

            for s in section_expanders:
                s.click()

            total_sections = len(section_expanders)
            reset_console_style()
            print(Fore.YELLOW + f'Total sections in this course: {total_sections}')
            print(Fore.YELLOW + f'Collecting video source URLs...')

            j = 0
            for i in range(total_sections):
                sub_list = []
                video_list = []
                video_title = ''
                j = i + 1
                main_section = driver.find_element_by_xpath(f"//div/section[{j}]/h3")
                sub_videos = driver.find_elements_by_xpath(f"//div/section[{j}]/ul[1]/li")
                for index, video in enumerate(sub_videos):
                    video_title = str(index) + "_" + video.text.split('\n')[0]
                    try:
                        anchor = video.find_element_by_xpath(".//a")
                        video_list.append([video_title, anchor.get_attribute('href')])
                    except NoSuchElementException as ne:
                        pass
                folder_list.append([main_section.text, video_list])

            for f in folder_list:
                for v in f[1]:
                    driver.get(v[1])
                    # wait for video element to load, sometimes video is loaded after the page loads
                    while not check_element_exists_by_xpath(driver, "//video"):
                        print(Fore.MAGENTA + 'Waiting for video to load..')
                        time.sleep(2)
                        waited_for_load_check = True

                    if waited_for_load_check:
                        waited_for_load_check = False
                        print(Fore.MAGENTA + 'Video loaded successfully. Continuing..')
                    video_element = driver.find_element_by_xpath("//video")
                    source_url = video_element.get_attribute('src')
                    v[1] = source_url
                    # print(f'Source URL: {v[1]}')
        except Exception as ve:
            print(Fore.RED + 'Error retrieving video source URL.')
            print(Fore.RED + str(ve))

        for section in folder_list:
            try:
                # print(os.path.join(os.getcwd(), f'{COURSE_NAME}', section[0]))
                os.makedirs(os.path.join(DOWNLOAD_PATH, f'{course[0]}', section[0]))
            except FileExistsError as fe:
                pass
            # download videos
            for v in section[1]:  # section[1] = [[Video title,URL], [Video title,URL], [Video title,URL], ...]
                print(Fore.YELLOW + f'Downloading video: {section[0]} - {v[0]}')
                video_to_download = Path(os.path.join(DOWNLOAD_PATH, f'{course[0]}', section[0], v[0] + ".mp4"))
                if video_to_download.is_file():
                    print(Fore.CYAN + f'Video {v[0]} already exists. Skipping to next')
                else:
                    urllib.request.urlretrieve(v[1], os.path.join(DOWNLOAD_PATH, f'{course[0]}', section[0], v[0] + ".mp4"))

        print(Fore.GREEN + f'Course {course_index+1}/{len(courses_to_download)}: {course[0]} downloaded successfully!')
        print(Back.GREEN + '___________________________________________________________________________________________________________________________')
        reset_console_style()
    print(Style.BRIGHT + Fore.BLUE + Back.WHITE + 'Finished downloading all courses!')
except Exception as e:
    print(Fore.RED + 'Error:')
    print(Fore.RED + str(e))
    exit(-1)
finally:
    driver.quit()
    pass

