import asyncio
import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# Telegram bot token
TELEGRAM_TOKEN = '7908485758:AAF4FFhU3LYxm6y9Pe7VSU-jjTqRLH3NORI'
bot = Bot(token=TELEGRAM_TOKEN)

active_users = set()
monitoring_active = True
application = None

# Event to control shutdown
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

async def graceful_shutdown():
    """Graceful shutdown for bot"""
    global monitoring_active, application
    print("Starting shutdown process...")
    monitoring_active = False
    
    if application:
        await application.stop()
        await application.shutdown()
    
    # Trigger shutdown event
    shutdown_event.set()
    
    print("Bot has been stopped successfully")

async def scrape_mostaql_projects():
    options = Options()
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

        # Send results to Telegram
        for i in range(len(title_list)):
            message_body = (
                f"New Project:\n"
                f"Title: {title_list[i]}\n"
                f"Description: {project_list[i]}\n"
                f"Price: {price_list[i]}\n"
                f"Duration: {time_list[i]}\n"
                f"Link: {links_list[i]}"
            )
            
            for chat_id in active_users:
                await send_message(chat_id, message_body)
                print(f"Message sent to chat_id: {chat_id}")

    except Exception as e:
        print(f"Error in scraping: {e}")
        raise

async def scrape_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text("Fetching projects from Mostaql...")

    try:
        await scrape_mostaql_projects()
        await update.message.reply_text("Projects fetched successfully!")
        # Notify shutdown
        await update.message.reply_text("Bot will be shut down now...")
        await asyncio.sleep(2)  # Short wait to ensure the message is sent
        await graceful_shutdown()
    except Exception as e:
        await update.message.reply_text(f"Error occurred while fetching projects: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in active_users:
        active_users.add(chat_id)
        await update.message.reply_text("Welcome! You have been successfully registered to receive projects.")
    else:
        await update.message.reply_text("You are already registered.")

async def main():
    global application
    
    # Initialize application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("scrape", scrape_command))

    # Start resource monitoring task
    monitor_task = asyncio.create_task(monitor_resources())
    
    try:
        # Initialize and start the application
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Wait for shutdown event
        await shutdown_event.wait()
        
    except Exception as e:
        print(f"Error in main loop: {e}")
    finally:
        # Cancel monitoring task
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        
        # Stop the application if not already stopped
        if application:
            try:
                await application.stop()
                await application.shutdown()
            except Exception as e:
                print(f"Error during shutdown: {e}")

if __name__ == "__main__":
    asyncio.run(main())
