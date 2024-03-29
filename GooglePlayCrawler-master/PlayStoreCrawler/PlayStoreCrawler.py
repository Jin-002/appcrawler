#!/usr/bin/python
# coding: utf-8
import re

import pandas as pd
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from time import sleep

from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PlayStoreCrawler.Utils import *
import traceback, time
import sys
from selenium.webdriver.common.by import By
import random
from selenium.webdriver import ActionChains
import csv

#This crawler actually print the comments with his related information about a given link of the Android Play Store
#It is so easy to use. Just use the command:
#	$python PlayStoreCrawler.py <link>
#Author:Francisco Javier Lendinez Tirado


#Open a Firefox window with the address given
def chargeDriver(address):
	#If you want to use Chrome, uncomment this following line
	#Driver = webdriver.Chrome("/path/to/chrome/driver")
	service = Service(executable_path="D:\\tools\\webdriver\\chromedriver")
	Driver = webdriver.Chrome()
	print(address)
	Driver.get(address)
	return Driver


def roll_window_to_bottom(browser, stop_length=None, step_length=500):
    """selenium 滚动当前页面，向下滑
    :param browser: selenium的webdriver
    :param stop_length: 滑动的最大值
    :param step_length: 每次滑动的值
    """
    original_top = 0
    while True:  # 循环向下滑动
        if stop_length:
            if stop_length - step_length < 0:
                browser.execute_script("window.scrollBy(0,{})".format(stop_length))
                break
            stop_length -= step_length
        browser.execute_script("window.scrollBy(0,{})".format(step_length))
        time.sleep(0.5 + random.random())  # 停顿一下
        check_height = browser.execute_script(
            "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")
        if check_height == original_top:  # 判断滑动后距顶部的距离与滑动前距顶部的距离
            break
        original_top = check_height


#Find and store the comments
def extractComments(Driver,AppName):
    elmt = Driver.find_element(By.XPATH, "//button[contains(@class,'VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-dgl2Hf ksBjEc lKxP2d LQeN7 aLey0c')]")
    elmt.click()  # 点击 see all reviews
    time.sleep(1)
    reviews_num = 0  # 保存的用户评论的条数
    elmt = Driver.find_element(By.CLASS_NAME, 'odk6He')
    # 向下滚动
    scroll_origin = ScrollOrigin.from_element(elmt)
    while reviews_num < 10000:
        file = open(AppName + '.csv', 'a', newline='', encoding='utf-8')
        csv_writer = csv.writer(file, delimiter=',')
        i = 10
        while i != 0:
            ActionChains(Driver).scroll_from_origin(scroll_origin, 0, 300000).perform()
            time.sleep(2)
            i = i - 1
        reviews = Driver.find_elements(By.CLASS_NAME, 'RHo1pe')
        start = reviews_num-1 if reviews_num != 0 else 0
        for review in reviews[start:]:
            t = review.find_element(By.XPATH, '//*[@class="bp9Aid"]')  # 评论时间
            review_time = t.text
            # 评论等级
            rate = review.find_element(By.CLASS_NAME, 'iXRFPc')
            review_rate = rate.get_attribute('aria-label')
            # 评论内容
            content = review.find_element(By.CLASS_NAME, 'h3YV2d')
            review_content = content.text
            csv_writer.writerow([review_time, review_rate, review_content])
        file.close()
        reviews_num = len(reviews)

#Execute all the functions
def MainProcess(address):
    if len(address):
        format = re.compile(r'id=(.+?)&hl=en_US')
        name = format.findall(address)[0]
        try:
            Driver = chargeDriver(address)
            extractComments(Driver, name)
            Driver.quit()
        except:
            traceback.print_exc()
            # raw_input("See the possible error and go in")
            Driver.quit()


#If you use the crawler as script and not as a library
if __name__ == '__main__':
    if (len(sys.argv) > 1):
        address = sys.argv[1]
    else:
        print("It needs an address")
        exit()
    MainProcess(address)
