"""
    58同城
"""


import time
from datetime import datetime
from pathlib import Path
import pandas as pd
from pandas import DataFrame
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from common.selenium_tools import ChromeHelper
from apscheduler.schedulers.background import BlockingScheduler
from common.sql_tools import MySqlHelper

def tongcheng_spider():
    count = 0
    image_dir = "58同城图片"+str(int(datetime.now().timestamp()))
    # 创建存储图片的文件夹
    Path(image_dir).mkdir(exist_ok=True)
    # if Path(file_name).exists():
    #     old_df = pd.read_excel(file_name)
    #进入网站搜索
    with ChromeHelper() as driver:
        driver.get(
            "https://hz.58.com/?utm_source=market&spm=u-2d2yxv86y3v43nkddh1.BDPCPZ_BT&pts=1719456601804")
        input_element = driver.wait_presence_of_element(By.XPATH, '//input[@id="keyword"]')
        input_element.send_keys("汽车")
        input_element.send_keys(Keys.ENTER)
        # if driver.wait_url_contains("login"):
        #     driver.wait_presence_of_element(By.XPATH, '//a[@href="https://passport.58.com/login/?path=https%3A%2F%2Fhz.58.com%2F%3Futm_source%3Dmarket%26spm%3Du-2d2yxv86y3v43nkddh1.BDPCPZ_BT%26pts%3D1719456954746&source=58-homepage-pc"]').click()
    # 向下滚动，显示图片
        for __ in range(10):
            driver.scroll_by(y = 500)
            time.sleep(1)
        list_element = driver.wait_presence_of_elements(By.XPATH,
                                                        '//div[@class="list-wrap"]//li[@class="info"]')
        # list_table = []
        for item in list_element:
            dict_row = {
                "汽车名称": item.find_element(By.XPATH, './/h2[@class="info_title"]').text,

            }
    # 增量爬虫   如果旧文件不在 或者 没在旧数据中
            if not sql_helper.fetch_one(
                    "select * from car where 汽车名称 = %s;", dict_row["汽车名称"]
                                        ):
                # list_table.append(dict_row)
    #多级页面采集
                # 进入详情页
                item.find_element(By.XPATH,'.//div[@class="info--wrap"]/a').click()
                driver.switch_window(-1)
                # 采集详情页
                # dict_row["上牌时间"] = driver.wait_presence_of_element(By.XPATH,'(//span[@class="info-conf_value"])[1]').text
                dict_row["表显里程"] = driver.wait_presence_of_element(By.XPATH,'(//span[@class="info-conf_value"])[2]').text
                # dict_row["上映时间"] = driver.wait_presence_of_element(By.XPATH,'//li[@class="ellipsis"][3]').text
                # 关闭详情页
                driver.close()
                # 切换回主页
                driver.switch_window(0)
    #图片下载
                url = item.find_element(By.XPATH,
                                       './/img[@class="info_pic"]').get_attribute(
                    "data-original")
                count += 1
                time.sleep(0.5)
                dict_row["图片名"]="%s/%s.jpg"%(image_dir,count)
                driver.download_image(url, dict_row["图片名"])

    # 向数据库插入新数据
                sql_helper.execute("insert into car values(0,%s,%s,%s);", *dict_row.values())
                print(dict_row)
        # target_df = DataFrame(list_table)
        # if Path(file_name).exists():
        #     target_df = pd.concat([old_df, target_df])
        # target_df.to_excel(file_name, index=False)

sql_helper=MySqlHelper("tongcheng")
tongcheng_spider()
#定时
# scheduler = BlockingScheduler()
# scheduler.add_job(tongcheng_spider(), "interval", minutes=15)  # hours minutes seconds
# scheduler.start()
sql_helper.close()