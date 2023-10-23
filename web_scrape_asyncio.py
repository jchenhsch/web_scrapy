import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth

async def scrape_comments():
   
    browser = await launch(headless=True)
    page = await browser.newPage()
    # await stealth(page)
    # await page.setViewport({'width':1200, 'height':800})
    
    #await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')


    # Block the video component from loading
    # await page.setRequestInterception(True)
    # page.on('request', lambda req: req.abort() if req.resourceType == 'video' else req.continue_())


    # Navigate to the YouTube video page
    await page.goto('https://www.youtube.com/watch?v=3ryID_SwU5E')

    # Wait for the comments section to load
    await page.waitForSelector('#snippet', timeout=15000)  # Wait for the #comments element
    # await page.waitForNavigation()
    
    # Infinite scroll until all comments are loaded
    previous_height = 0
    while True:
        current_height = await page.evaluate('document.documentElement.scrollHeight')
        await page.evaluate('window.scrollTo(0, document.documentElement.scrollHeight)')
        print("scrolling")

        await page.waitForSelector('#comments', timeout=15000)
          
        await asyncio.sleep(20)
        # Extract comments
        
        
        if current_height == previous_height:
                break  # No new content loaded, break the loop
        previous_height = current_height
        await page.evaluate('window.scrollTo(0, document.documentElement.scrollHeight)')
    
    comments = await page.evaluate('''() => {
            const commentElements = document.querySelectorAll('#content-text');
            return Array.from(commentElements, commentElement => commentElement.textContent);
        }''')
        

    print(f'Number of comments: {len(comments)}')

    page_source = await page.content()
    with open('youtube_page.html', 'w', encoding='utf-8') as html_file:
        html_file.write(page_source)

    # Save comments to a file
    with open('comments.txt', 'w', encoding='utf-8') as file:
        file.write('\n'.join(comments))

    # Close the browser
    await browser.close()

# Run the scraping function
asyncio.get_event_loop().run_until_complete(scrape_comments())
