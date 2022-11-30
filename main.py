import os
import logging
import telegram

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from telegram.ext import Updater, CommandHandler
from time import sleep
from selenium.webdriver.chrome.options import Options

my_secret = os.environ['TELEGRAM_BOT_TOKEN']

PHOTO_PATH = 'screenshot.png'
CHROMEDRIVER_PATH = os.getenv('$HOME')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Привет! Для получения расписания воспользуйся командой "/ladno".')


def ladno(update, context):
    update.message.reply_text('Подождём 10-20 секунд!')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    URL = 'http://timetable.msu.az'
    driver.get(URL)
    username = driver.find_element_by_name("username")
    username.clear()
    username.send_keys("username")
    password = driver.find_element_by_name("password")
    password.clear()
    password.send_keys("password")
    driver.find_element_by_name("submit").click()
    driver.find_element_by_id("tdMenu").click()
    driver.find_element_by_id("tdeduGraph_common").click()
    sleep(5)
    select = Select(driver.find_element_by_id("repProfId"))
    select.select_by_value("10")
    sleep(2)
    select = Select(driver.find_element_by_id("repCourseId"))
    select.select_by_value("2")
    sleep(8)
    element = driver.find_element_by_xpath("//select[@name='repWeekId']")
    all_options = element.find_elements_by_tag_name("option")
    for option in all_options:
      option.click()
    driver.find_element_by_name("repGraph").click()

    sleep(6)
    S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
    driver.set_window_size(S('Width'),S('Height'))
    driver.find_element_by_tag_name('body').screenshot('screenshot.png')
    driver.quit()
    bot = telegram.Bot(token=my_secret)
    bot.send_message(chat_id=update.message.chat_id, text="Держи Расписание")
    bot.send_photo(chat_id=update.message.chat_id,photo=open(PHOTO_PATH, 'rb'))
    os.remove("screenshot.png")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    
    updater = Updater(my_secret, use_context=True)

   
    dp = updater.dispatcher

    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ladno", ladno))

   
    dp.add_error_handler(error)

    
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
