from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time


# Initialize a web driver instance to control a Chrome window
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()),
    options=options
)
url = 'https://www.youtube.com/watch?v=ktyJIj6i4Qw'
driver.get(url)

driver.implicitly_wait(30)

try:
    driver.find_element(By.ID, 'description-inline-expander').click()
except:
    pass

driver.execute_script("window.focus();")
driver.maximize_window()
driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")


video = {}
WebDriverWait(driver, 60).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.ytd-watch-metadata'))
        )
title = driver \
    .find_element(By.CSS_SELECTOR, 'h1.ytd-watch-metadata') \
    .text

channel = {}

# scrape the channel info attributes
channel_element = driver \
    .find_element(By.ID, 'owner')

channel_url = channel_element \
              .find_element(By.CSS_SELECTOR, 'a.yt-simple-endpoint') \
              .get_attribute('href')
channel_name = channel_element \
              .find_element(By.ID, 'channel-name') \
              .text
channel_image = channel_element \
              .find_element(By.ID, 'img') \
              .get_attribute('src')
channel_subs = channel_element \
              .find_element(By.ID, 'owner-sub-count') \
              .text \
              .replace(' subscribers', '')

channel['url'] = channel_url
channel['name'] = channel_name
channel['image'] = channel_image
channel['subs'] = channel_subs

# click the description section to expand it
driver.find_element(By.ID, 'description-inline-expander').click()

info_container_elements = driver \
    .find_elements(By.CSS_SELECTOR, '#info-container span')
views = info_container_elements[0] \
    .text \
    .replace(' views', '')
publication_date = info_container_elements[2] \
    .text

description = driver \
    .find_element(By.CSS_SELECTOR, '#description-inline-expander .ytd-text-inline-expander span') \
    .text

likes = driver \
    .find_element(By.ID, 'segmented-like-button') \
    .text

video['url'] = url
video['title'] = title
video['channel'] = channel
video['views'] = views
video['publication_date'] = publication_date
video['description'] = description
video['likes'] = likes
print(video)





    
    