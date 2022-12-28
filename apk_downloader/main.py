import json
import threading
from threading import Thread
from multiprocessing import JoinableQueue

import dataset
import pika
import time
import undetected_chromedriver as uc


from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from threading import Thread
from loguru import logger

from config import pgdb, pguser, pgpass, pghost, pgport, apk_save_folder
from helper import every_downloads_chrome, wait_page_download_finished


jobs = JoinableQueue()

db = dataset.connect(f'postgresql://{pguser}:{pgpass}@{pghost}:{pgport}/{pgdb}')
table = db['apk']

def download_apks(q):
    while True:
        value = q.get()
        if not value:
            break
        
        logger.info(f'received new task {value}')
        url = value['download_link']


        params = {"behavior": "allow","downloadPath": apk_save_folder}

        driver = uc.Chrome(headless = False, service_log_path=None)
        driver.execute_cdp_cmd("Page.setDownloadBehavior", params)
        driver.set_window_size(200, 400)
        driver.get(url)
        
        wait_page_download_finished(driver)
        WebDriverWait(driver, 300, 1).until(every_downloads_chrome)
        table.insert(value)
        driver.close()
        q.task_done()


for i in range(5):
    apk_downloader = threading.Thread(target=download_apks, args=(jobs,))
    apk_downloader.daemon = True
    apk_downloader.start()
    apk_downloader.join(0)
    
def callback(ch,method,properties,body):
    logger.info('received message')
    message = json.loads(body.decode('utf-8'))
    jobs.put(message)
    
    
connection= pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel= connection.channel()
channel.basic_consume(queue='item', on_message_callback=callback, auto_ack=True)

t1 = Thread(target= channel.start_consuming)
t1.start()
t1.join(0)
