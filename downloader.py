
import base64
import os
import requests
import time
import click
from tqdm import tqdm

from io import BytesIO
from PIL import Image
from PIL import UnidentifiedImageError
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from rq import Queue
from redis import Redis

from utils.process_image import process
from utils.tools import check_if_result_b64, get_save_location
from utils.driver import get_options

redis_conn = Redis()
q = Queue(connection=redis_conn) 

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
CHROME_DRIVER_LOCATION = os.path.join(PROJECT_ROOT, "chromedriver")


def get_driver(term):
    new_driver = webdriver.Chrome(executable_path=CHROME_DRIVER_LOCATION, options=get_options())
    # new_driver = webdriver.Firefox(executable_path = DRIVER_BIN_FIRE)
    new_driver.get(f"https://www.google.com/search?q={'+'.join(term)}&source=lnms&tbm=isch&sa=X")
    return new_driver


@click.command()
@click.argument('search')
@click.argument('limit')
def get_images(search, limit):
    driver = get_driver(search.split())

    first_search_result = driver.find_elements_by_xpath('//a/div/img')[0]
    first_search_result.click()

    right_panel_base = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'''//*[@data-query="{' '.join(search.split())}"]''')))
    first_image = right_panel_base.find_elements_by_xpath('//*[@data-noaft="1"]')[0]
    magic_class = first_image.get_attribute('class')
    image_finder_xp = f'//*[@class="{magic_class}"]'
    

    # initial wait for the first image to be loaded
    # this part could be improved but I couldn't find a proper way of doing it
    time.sleep(3)
    # initial thumbnail for "to_be_loaded image"
    thumbnail_src = driver.find_elements_by_xpath(image_finder_xp)[-1].get_attribute("src")

    for i in tqdm(range(int(limit))):

        # issue 4: All image elements share the same class. Assuming that you always click "next":
        # The last element is the base64 encoded thumbnail version is of the "next image"
        # [-2] element is the element currently displayed
        target = driver.find_elements_by_xpath(image_finder_xp)[-2]

        # you need to wait until image is completely loaded:
        # first the base64 encoded thumbnail will be displayed
        # so we check if the displayed element src match the cached thumbnail src.
        # However sometimes the final result is the base64 content, so wait is capped
        # at 5 seconds.
        wait_time_start = time.time()
        while (target.get_attribute("src") == thumbnail_src) and time.time() < wait_time_start + 5:
            time.sleep(0.2)
        thumbnail_src = driver.find_elements_by_xpath(image_finder_xp)[-1].get_attribute("src")
        attribute_value = target.get_attribute("src")
        # print(attribute_value)
        loc = get_save_location(search.split())
        q.enqueue(process, i, attribute_value, loc)
        # process_image(attribute_value)
        # issue 3: this Xpath is bad """//*[@id="Sva75c"]/div/div/div[3]/div[2]/div/div[1]/div[1]/div/div[1]/a[2]/div""" if page layout changes, this path breaks instantly
        svg_arrows_xpath = '//div[@jscontroller]//a[contains(@jsaction, "click:trigger")]//*[@viewBox="0 0 24 24"]'
        next_arrow = driver.find_elements_by_xpath(svg_arrows_xpath)[-3]
        # print(next_arrow.location['y'])
        # driver.execute_script("window.scrollTo(0,"+str(next_arrow.location['y'])+")");

        next_arrow.click()

if __name__ == "__main__":
    get_images()
