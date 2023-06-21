import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import urllib
import time

WORD='ホンドギツネ'
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
# Create url variable containing the webpage for a Google image search.
url = ("https://www.google.com/search?q={s}&tbm=isch&tbs=sur%3Afc&hl=en&ved=0CAIQpwVqFwoTCKCa1c6s4-oCFQAAAAAdAAAAABAC&biw=1251&bih=568")
# Launch the browser and open the given url in the webdriver.
driver.get(url.format(s=WORD))
# Scroll down the body of the web page and load the images.
driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
time.sleep(5)
# Find the images.
imgResults = driver.find_elements(By.XPATH,"//img[contains(@class,'Q4LuWd')]")
# Access and store the scr list of image url's.
src = []
for img in imgResults:
    src.append(img.get_attribute('src'))
# Retrieve and download the images.
for i in range(1000):    urllib.request.urlretrieve(str(src[i]),"sample_data2/{}_{}.jpg".format(WORD, i))