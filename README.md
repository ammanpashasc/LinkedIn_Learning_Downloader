# LinkedIn_Learning_Downloader
A Python script to download courses from LinkedIn Learning. For educational use only!

##### Dependencies:
- Python 3.x
- selenium
- colorama
- lxml
- chromedriver

##### Info

- Please use this script for your own purposes, at your own risk.
- This script was written for educational usage only.

##### Usage
1. > pip install -r requirements.txt

2. Edit `config.json` to include chromedriver settings and courses you want to download
   
   Chromedriver settings: 
   ```
    chromeDriverLocation: Location to your chromedriver executable.
    runHeadless: Set to `true` if you want to run the chromedriver in headless mode.
    ```
    
    Courses to download:
    ```
    url: https://www.linkedin.com/learning/python-advanced-design-pattern
    title: Python Advanced Design Patterns
    ```
3.  >python generate_cookies.py
    
    To generate cookies by logging into your LinkedIn account.

4. Once cookies are generated, run the scraper
    > python scraper.py



##### TODO

 - Add subtitles
 - Implement threading and async downloads