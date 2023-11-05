import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth
import random
import os
import re
import csv
from latest_user_agents import get_latest_user_agents, get_random_user_agent
from youtube_search import get_youtube_search_links
import concurrent.futures

async def create_agent(USER_AGENTS):
    user_agent = random.choice(USER_AGENTS)
    browser = await launch(headless=True,args=[f'--user-agent={user_agent}','--disable-setuid-sandbox', '--no-sandbox', '--disable-extensions'])
    page = await browser.newPage()
    await(stealth(page))
    return page, browser

async def close_agent(browser, page):
    await page.close()
    await browser.close()

async def scrape_comments(page, video_url):
    try:

        print(f"Processing video: {video_url}")

        await page.goto(video_url, {'waitUntil': 'domcontentloaded'})
        
        # Extract information from the expanded description section
        
        info_container_elements = await page.querySelectorAll('#info-container span')
        likes_element = await page.waitForSelector('#segmented-like-button')
        description_element = await page.querySelector('#description-inline-expander .ytd-text-inline-expander span')
        
        info_container_elements = await page.querySelectorAll('#info-container span')
        
        # get video title
        video_title_element = await page.querySelector('#title > h1 > yt-formatted-string')

        if video_title_element:
            video_title = await page.evaluate('(element) => element.textContent', video_title_element)
            #print(video_title)
        else:
            print('Video title element not found')


        # Check if the elements exist before accessing their properties
        if len(info_container_elements) > 0:
            views_element = info_container_elements[0]
            views = await (await views_element.getProperty('textContent')).jsonValue()
            views = views.replace(' views', '')
        else:
            views = 'N/A'
        
        if len(info_container_elements) > 2:
            publication_date_element = info_container_elements[2]
            publication_date = await (await publication_date_element.getProperty('textContent')).jsonValue()
        else:
            publication_date = 'N/A'
        
        description = await (await description_element.getProperty('textContent')).jsonValue()
        likes_element = await page.querySelector('#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button')
        aria_label = await page.evaluate('(element) => element.getAttribute("aria-label")', likes_element)
        print(aria_label)
        likes_match = re.search(r'\b\d[\d,.]*\d\b', aria_label)  # Match one or more digits
        likes = likes_match.group() if likes_match else 'N/A'
        print(likes)


        
        channel_element = await page.waitForSelector('#owner')

        channel_url = await page.evaluate('(element) => element.querySelector("a.yt-simple-endpoint").href', channel_element)
        channel_name = await page.evaluate('(element) => element.querySelector("#text").title', channel_element)
        # print(channel_name)
        channel_image = await page.evaluate('(element) => element.querySelector("#img").getAttribute("src")', channel_element)
        
        channel_subs_element = await page.querySelector('#owner-sub-count')
        channel_subs = await page.evaluate('(element) => element ? element.textContent.replace(" subscribers", "") : "N/A"', channel_subs_element)
        
        
        # get comments 
        # Wait for the comments section to load
        await page.waitForSelector('#sections', timeout=150000)  # Wait for the #comments element
        # await page.waitForNavigation()
        
        # Infinite scroll until all comments are loaded
        previous_height = 0
        while True:
            current_height = await page.evaluate('document.documentElement.scrollHeight')
            await page.evaluate('window.scrollTo(0, document.documentElement.scrollHeight)')
            #print("scrolling")

            await page.waitForSelector('#comments', timeout=150000)
            
            await asyncio.sleep(random.uniform(3, 7))
            # Extract comments
            
            if current_height == previous_height:
                break  # No new content loaded, break the loop
            previous_height = current_height
            await page.evaluate('window.scrollTo(0, document.documentElement.scrollHeight)')
        
        comments = await page.evaluate('''() => {
                const commentElements = document.querySelectorAll('#content-text');
                return Array.from(commentElements, commentElement => commentElement.textContent);
            }''')
        print(f'Number of comments for {video_url}: {len(comments)}')
        
        
        
        # Write video_info, channel_info, and comments to CSV file

        with open('comments_'+ keyword + '.csv', 'a', newline='', encoding='utf-8') as csvfile:
            is_empty = os.path.getsize('comments_'+ keyword + '.csv') == 0
            csv_writer = csv.writer(csvfile)
            if is_empty:
                csv_writer.writerow(['Video Title', 'Video URL', 'Views', 'Publication Date', 'Description', 'Likes', 'Channel URL', 'Channel Name', 'Channel Image', 'Channel Subscribers', 'Comments'])
            for comment in comments:
                csv_writer.writerow([video_title, video_url, views, publication_date, description, likes, channel_url, channel_name, channel_image, channel_subs, comment])
    except:
        pass   

async def main(video_links,keyword = 'chinese economy'):
    USER_AGENTS = get_random_user_agent()
    tasks = []
    agents = []
    
    async def scrape_comments_wrapper(video_url):
        page, browser = await create_agent(USER_AGENTS)
        try:
            await scrape_comments(page, video_url)
        except Exception as e:
            print(f"Error processing {video_url}: {e}")
        finally:
            await close_agent(browser, page)

   # assign the threads to perform asyncio / concurrent task
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Use executor to run scrape_comments_wrapper concurrently for each video link
        await asyncio.gather(*[executor.submit(scrape_comments_wrapper, video_url) for video_url in video_links])

    for page, browser in agents:
        await close_agent(browser, page)

# List of video links to scrape comments from

keyword = 'Chinese economy'
video_links = asyncio.get_event_loop().run_until_complete(get_youtube_search_links(keyword))
sublists = [video_links[i:i + 15] for i in range(0, len(video_links), 10)]
# Run the scraping function with the list of video links
for sublist in sublists:
    asyncio.get_event_loop().run_until_complete(main(sublist,keyword))
