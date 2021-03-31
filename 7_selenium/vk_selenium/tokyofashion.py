from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from pymongo import MongoClient
from selenium import webdriver
from time import sleep
import re


def record_to_mongo(item, collection):
    collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)


def scroll_to_end(driver):
    sleep(1)
    while True:
        try:
            not_now = driver.find_element_by_class_name('JoinForm__notNow')
            not_now.click()
        except NoSuchElementException:
            pass
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)
        if 'none' in driver.find_element_by_id('fw_load_more').get_attribute('style'):
            break


def get_media(links):
    media = list()
    if links:
        for l in links:
            video_link = l.get_attribute('href')
            if video_link:
                media.append(video_link)
            else:
                image_link = re.findall('https.+\w', l.get_attribute('style'))[0]
                media.append(image_link)
    else:
        media = None

    return media


def get_item(container):
    item = dict()
    item['date'] = container.find_element_by_class_name("rel_date").text
    item['text'] = container.find_element_by_class_name("wall_post_text").text
    sleep(1)
    item['link'] = container.find_element_by_class_name("post_link").get_attribute('href')
    media_links = container.find_elements_by_class_name("image_cover")
    item['media'] = get_media(media_links)

    likes = container.find_element_by_class_name('like').text
    if likes:
        item['likes'] = int(likes)

    shares = container.find_element_by_class_name('share').text
    if shares:
        item['shares'] = int(shares)

    # item['views'] = ''.join([x for x in driver.find_element_by_xpath('//div[contains(@class, "_views")]')
    #                         .get_attribute('title') if x.isdigit()])
    item['views'] = driver.find_element_by_class_name('_views').text.replace('.', '').replace('K', '000')
    return item


MONGO_URL = 'localhost:27017'
client = MongoClient(MONGO_URL)
db = client.vk

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--headless")
driver_path = '../chromedriver'
driver = webdriver.Chrome(options=chrome_options, executable_path=driver_path)
url = 'https://vk.com/tokyofashion'

driver.get(url)

search = input('What do you wanna find?>> ')
search_href = driver.find_element_by_class_name('ui_tab_search').get_attribute('href')
driver.get(search_href)
driver.find_element_by_id('wall_search').send_keys(search)
driver.find_element_by_id('wall_search').send_keys(Keys.ENTER)
sleep(1)
driver.find_element_by_class_name('_ui_toggler').click()

scroll_to_end(driver)

posts = driver.find_elements_by_class_name("post--with-likes")
if len(posts) == 0:
    print('nothing found')
else:
    for post in posts:
        record_to_mongo(get_item(post), db[search])
