import scrapy
from bs4 import BeautifulSoup
import json
from scrapy_weather.items import HuxiuItem

class WeatherSpider(scrapy.Spider):
    name = 'huxiu'
    allowed_domains = ['huxiu.com']
    start_urls = ['https://huxiu.com/']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    def parse(self, response):
        item=HuxiuItem()
        #print("here in parsing")
        soup = BeautifulSoup(response.body, 'html.parser')

        #content_lst = soup.find_all(class_="tibt-card__top")
        content_lst = soup.find_all(class_="home-news-module__article-list__item tibt-card")
        for ele in content_lst:
            div_top= ele.find(class_="tibt-card__top__img-wrap")
            #print(div_top)
            item["title"] = div_top.find("img")['alt']
            div_buttom = ele.find(class_="tibt-card__bottom")
            div_href = div_buttom.find(class_ = "tibt-card__bottom__title-wrap")['href']
            item["link"] = self.start_urls[0]+str(div_href[1:])
            div_status = ele.find(class_="tibt-card__bottom__status-wrap vertical-center")
            div_time = div_status.find(class_="status__date").text
            item["posttime"] = div_time

            print(item["title"],item["link"],item["posttime"],"\n")
    
            #print(ele.prettify())
        

        