import asyncio
import os
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# Get token from environment variable
TELEGRAM_TOKEN = os.getenv('7908485758:AAF4FFhU3LYxm6y9Pe7VSU-jjTqRLH3NORI')
if not TELEGRAM_TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found in environment variables")

bot = Bot(token=TELEGRAM_TOKEN)

active_users = set()
running = True
monitoring_active = True

async def send_message(chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)

async def monitor_resources():
    while monitoring_active:
        try:
            cpu_usage = psutil.cpu_percent()
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
            print(f"CPU Usage: {cpu_usage}% | Memory Usage: {memory_usage}%")
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in resource monitoring: {e}")
            await asyncio.sleep(10)

async def scrape_mostaql_projects():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Setup Firefox service with geckodriver
    service = Service(GeckoDriverManager().install())

    title_list = []
    project_list = []
    price_list = []
    time_list = []
    links_list = []

    try:
        with webdriver.Firefox(options=options, service=service) as driver:
            url = 'https://mostaql.com/projects'
            driver.get(url)

            for scrap in range(1, 16):
                try:
                    row = driver.find_element(By.XPATH, f'(//h2)[{scrap}]')
                    link = row.find_element(By.XPATH, './a')
                    alink = link.get_attribute('href')
                    link.click()

                    await asyncio.sleep(2)

                    title = driver.find_element(By.TAG_NAME, 'h1').text
                    project = driver.find_element(By.XPATH, '//*[@id="project-brief-panel"]').text
                    price = driver.find_element(By.CSS_SELECTOR, '#project-meta-panel > div:nth-child(1) > table > tbody > tr:nth-child(3) > td:nth-child(2) > span').text
                    time_value = driver.find_element(By.CSS_SELECTOR, '#project-meta-panel > div:nth-child(1) > table > tbody > tr:nth-child(4) > td:nth-child(2)').text
                    
                    title_list.append(title)
                    project_list.append(project)
                    price_list.append(price)
                    time_list.append(time_value)
                    links_list.append(alink)

                    driver.back()
                    await asyncio.sleep(2)

                except NoSuchElementException as e:
                    print(f'Element not found for scrap {scrap}: {e}')
                    continue

        for i in range(len(title_list)):
            message_body = (
                f"مشروع جديد: \n"
                f"العنوان: {title_list[i]}\n"
                f"الوصف: {project_list[i]}\n"
                f"السعر: {price_list[i]}\n"
                f"المدة: {time_list[i]}\n"
                f"الرابط: {links_list[i]}"
            )
            
            for chat_id in active_users:
                await send_message(chat_id, message_body)
                print(f"Message sent to chat_id: {chat_id}")

    except Exception as e:
        print(f"Error in scraping: {e}")
        raise

async def scrape_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text("جاري جلب المشاريع من مستقل...")

    try:
        await scrape_mostaql_projects()
        await update.message.reply_text("تم جلب المشاريع بنجاح!")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء جلب المشاريع: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in active_users:
        active_users.add(chat_id)
        await update.message.reply_text("مرحبًا بك! تم تسجيلك بنجاح لاستلام المشاريع.")
    else:
        await update.message.reply_text("أنت بالفعل مسجل.")

async def shutdown(application: Application):
    global monitoring_active, running
    monitoring_active = False
    running = False
    await application.stop()
    await application.shutdown()

def signal_handler():
    global running
    running = False

async def main():
    global running
    
    # Set up signal handlers
    import signal
    signal.signal(signal.SIGINT, lambda s, f: signal_handler())
    signal.signal(signal.SIGTERM, lambda s, f: signal_handler())
    
    # Set up application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("scrape", scrape_command))

    # Start monitoring task
    monitor_task = asyncio.create_task(monitor_resources())
    
    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        while running:
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        await shutdown(application)
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
