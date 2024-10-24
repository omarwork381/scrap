The code you've provided is a Telegram bot that uses Selenium to scrape project listings from a site called "Mostaql". In order to ensure that the bot runs and listens for the `/scrape` command, and then shuts down until another `/scrape` command is received, you can implement an event loop that waits for the command and manages the lifecycle of the Selenium browser instance as well as the Telegram bot.

Here’s how you can refine your existing code for better management of the bot's lifecycle and command handling:

```python
import asyncio
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import sys

TELEGRAM_TOKEN = '7908485758:AAF4FFhU3LYxm6y9Pe7VSU-jjTqRLH3NORI'  # Replace with your actual token
bot = Bot(token=TELEGRAM_TOKEN)

active_users = set()
monitoring_active = True
application = None
shutdown_event = asyncio.Event()

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
    options.headless = True

    title_list = []
    project_list = []
    price_list = []
    time_list = []
    links_list = []

    try:
        with webdriver.Firefox(options=options) as driver:
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

async def scrape_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text("جاري جلب المشاريع من مستقل...")

    try:
        await scrape_mostaql_projects()
        await update.message.reply_text("تم جلب المشاريع بنجاح!")
        await graceful_shutdown()  # Invoke shutdown after scraping
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء جلب المشاريع: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in active_users:
        active_users.add(chat_id)
        await update.message.reply_text("مرحبًا بك! تم تسجيلك بنجاح لاستلام المشاريع.")
    else:
        await update.message.reply_text("أنت بالفعل مسجل.")

async def graceful_shutdown():
    global monitoring_active
    print("بدء عملية الإيقاف...")
    monitoring_active = False
    shutdown_event.set()
    print("تم إيقاف البوت بنجاح")

async def main():
    global application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("scrape", scrape_command))

    # Start resource monitoring
    monitor_task = asyncio.create_task(monitor_resources())
    
    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        await shutdown_event.wait()  # Wait for shutdown event

    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        # Cancel monitor task
        monitor_task.cancel()
        await monitor_task  # Ensure it has finished
        if application:
            await application.stop()
            await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### Key Changes:
1. **Graceful Shutdown**: The `graceful_shutdown()` function now stops the resource monitoring and sets the shutdown event.
2. **Lifecycle Management**: The bot starts and waits for the shutdown event, allowing it to end cleanly after scraping.
3. **Error Handling**: Added try-except blocks to capture errors during bot operations.

### Note:
- Make sure to replace `'your_telegram_token_here'` with your actual Telegram bot token.
- For continuous operation using GitHub Actions or similar, ensure your bot's environment supports persistent connections and the necessary libraries (like `selenium` and `psutil`).
