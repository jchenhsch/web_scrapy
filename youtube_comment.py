from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time

# Initialize the web driver
options = webdriver.ChromeOptions()
options.add_argument("--disable-images")
options.add_argument("--disable-webgl")
options.add_argument("--disable-popup-blocking")
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)

# Navigate to the YouTube video page
driver.get("https://www.youtube.com/watch?v=ktyJIj6i4Qw")

# Wait for the comments section to load (you might need to adjust the wait time)
wait = WebDriverWait(driver, 15)
# get the focus of the window and maximize the window
driver.switch_to.window(driver.window_handles[0])
driver.maximize_window()

# scroll to the buttom hoping to grab the comment sections and triggers that to load
driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")


# Wait for the YouTube Premium pop-up and close it if it appears
try:
    youtube_premium_popup = wait.until(EC.presence_of_element_located((By.ID, 'premium-upsell-dialog-title')))
    close_button = driver.find_element(By.CLASS_NAME, 'style-scope.yt-button-renderer.style-text.size-small')
    close_button.click()
except TimeoutException:
    pass  # Continue if no premium pop-up is found

try:
    # Wait for the pop-up to appear (adjust the timeout value as needed)
    tv_promotion_popup = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[text()='Dismiss']")))

    # Execute JavaScript to click the "Dismiss" button and close the pop-up
    driver.execute_script("arguments[0].click();", tv_promotion_popup)

except Exception as e:
    pass

# Infinite scroll until all comments are loaded
# while True:
#     try:
#         element = driver.find_element(By.XPATH, '//*[@id="sections"]')
#         break
#     except Exception as e:
#         # Scroll down to the bottom using JavaScript
#         driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
#         # Wait for a brief moment to allow new content to load (adjust sleep duration if needed)
#         driver.implicitly_wait(2)
#         continue

# Scroll to the comment section and make sure it is visible for it to load
element = driver.find_element(By.XPATH, '//*[@id="sections"]')
driver.execute_script("arguments[0].scrollIntoView(true)",element)
time.sleep(5)


while True:
    # Get the current height of the page
    current_height = driver.execute_script("return document.documentElement.scrollHeight")
    
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    
    try:
        # Wait for the page to load new content
        
        time.sleep(5)
        # Calculate the new height of the page after loading new content
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        print("scrolling")
        # Break the loop if the page did not scroll (no new content loaded)
        if new_height == current_height:
            break
    except TimeoutException:
        # Break the loop if no more comments are loaded
        print("In Timeout exceptions")
        break

# Extract comments
while True:
    try:
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="content-text"]')))
        break
    except:
        time.sleep(10)
        continue

html_content = driver.page_source

# Use BeautifulSoup to parse the HTML content
soup = BeautifulSoup(html_content, "html.parser")

# Find all comment elements
comment_elements = soup.find_all("yt-formatted-string", class_="style-scope ytd-comment-renderer")

# Extract comments and replies
comments = []
for comment_element in comment_elements:
    comment_text = comment_element.text
    comments.append(comment_text)
print(len(comments))

# Save comments to a file
with open("comments.txt", "w", encoding="utf-8") as file:
    for comment in comments:
        file.write(comment + "\n")

# Close the browser window
driver.quit()


