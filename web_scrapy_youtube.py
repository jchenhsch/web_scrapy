import asyncio
from pyppeteer import launch
import csv
import json

async def scrape_youtube_data():
    browser = await launch(headless=True)
    page = await browser.newPage()

    # Navigate to the YouTube video page
    await page.goto('https://www.youtube.com/watch?v=3ryID_SwU5E')

    # Wait for the video details and comments section to load
    await page.waitForSelector('h1.ytd-watch-metadata', timeout=15000)

    # Extract video title, likes, and description
    video_title_element = await page.querySelector('h1.ytd-watch-metadata')
    video_title = await page.evaluate('(element) => element.textContent', video_title_element)
    print("vid_title",video_title)

    likes_element = await page.querySelector('#segmented-like-button')
    likes = await page.evaluate('(element) => element.textContent', likes_element)
    print("likes", likes)
    
    await page.click('#expand')
    description_element = await page.querySelector("#description-inline-expander .ytd-text-inline-expander span")
    description = await page.evaluate('(element) => element.textContent', description_element)
    print("desc",description)

    # Infinite scroll until all comments are loaded
    previous_height = 0
    while True:
        current_height = await page.evaluate('document.documentElement.scrollHeight')
        await page.evaluate('window.scrollTo(0, document.documentElement.scrollHeight)')
        #print("scrolling")
        await asyncio.sleep(5)  # Wait for 5 seconds between scrolls
        
        if current_height == previous_height:
            break  # No new content loaded, break the loop
        previous_height = current_height

    # Extract comments and their replies
    comments = await page.evaluate('''() => {
        const commentElements = document.querySelectorAll('#content-text');
        const comments = [];
        commentElements.forEach(commentElement => {
            const commentText = commentElement.textContent;
            const replyElements = commentElement.closest('#comment').querySelectorAll('#content-text');
            const replies = Array.from(replyElements, replyElement => replyElement.textContent);
            comments.push({ comment: commentText, replies: replies });
        });
        return comments;
    }''')

    print(f'Number of comments: {len(comments)}')

    # Save video data, comments, and replies to a CSV file
    data = []
    comment_elements = await page.querySelectorAll('#content-text')
    for comment_element in comment_elements:
        comment_text = await page.evaluate('(element) => element.textContent', comment_element)
        replies = []
        reply_elements = await comment_element.xpath('./ancestor::ytd-comment-renderer//yt-formatted-string[@id="content-text"]')
        for reply_element in reply_elements:
            reply_text = await page.evaluate('(element) => element.textContent', reply_element)
            replies.append(reply_text)
        data.append({'comment': comment_text.strip(), 'replies': replies})

    # Save data as JSON
    with open('youtube_data.json', 'w', encoding='utf-8') as json_file:
        json.dump({'video_title':video_title,'likes':likes,'description':description, 'comments': data}, json_file, ensure_ascii=False, indent=4)
    # Close the browser
    await browser.close()

    # Close the browser
    await browser.close()

# Run the scraping function
asyncio.get_event_loop().run_until_complete(scrape_youtube_data())
