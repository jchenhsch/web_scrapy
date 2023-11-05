import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth

async def get_youtube_search_links(keyword):
    browser = await launch(headless=True)
    page = await browser.newPage()
    await(stealth(page))

    # Navigate to the YouTube search results page with the specific keyword
    search_url = f'https://www.youtube.com/results?search_query={keyword}'
    await page.goto(search_url)

    # Wait for the search results to load
    await page.waitForSelector('#contents')

    # Infinite scroll until all search results are loaded (adjust the number of scrolls as needed)
    for _ in range(40):
        await page.evaluate('window.scrollTo(0, document.documentElement.scrollHeight);')
        await asyncio.sleep(2)  # Wait for 2 seconds between scrolls

    # Extract video links from the search results
    video_links = await page.evaluate('''() => {
        const links = [];
        const videoElements = document.querySelectorAll('#contents ytd-video-renderer');
        videoElements.forEach(videoElement => {
            const linkElement = videoElement.querySelector('a#thumbnail');
            if (linkElement) {
                const link = linkElement.getAttribute('href');
                const videoIdMatch = link.match(/(\/watch\?v=)([a-zA-Z0-9_-]{11})/);
                if (videoIdMatch && videoIdMatch[2]) {
                    links.push(`https://www.youtube.com/watch?v=${videoIdMatch[2]}`);
                }
            }
        });
        return links;
    }''')


    # Close the browser
    await browser.close()
    print (len(video_links))
    return video_links

# Run the function and print the list of video links
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(get_youtube_search_links('china'))
