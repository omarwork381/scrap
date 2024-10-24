import asyncio
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler
import pandas as pd

# Telegram bot token
TELEGRAM_TOKEN = '7908485758:AAF4FFhU3LYxm6y9Pe7VSU-jjTqRLH3NORI'  # Replace with your bot token
bot = Bot(token=TELEGRAM_TOKEN)

# Global variable to store user chat IDs
chat_ids = set()

# Command to start and register a user's chat ID
async def start(update: Update, context):
    chat_id = update.message.chat_id
    chat_ids.add(chat_id)
    await update.message.reply_text("You're now registered! Use /scrape to start scraping projects.")

# Command to scrape data and send to users, and stop the bot after sending messages
async def scrape(update: Update, context):
    await update.message.reply_text("Starting to scrape projects, please wait...")

    # Scrape the projects
    scraped_data = await scrape_projects()

    # Send the scraped data to all registered users
    for chat_id in chat_ids:
        for message_body in scraped_data:
            await bot.send_message(chat_id=chat_id, text=message_body)
            print(f"Message sent to Telegram chat_id: {chat_id}")

    # Stop the bot after sending messages
    await context.application.stop()
    print("Bot has stopped after sending messages.")

async def scrape_projects():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    url = 'https://mostaql.com/projects'
    driver.get(url)

    title_list = []
    project_list = []
    price_list = []
    time_list = []
    links_list = []

    for scrap in range(1, 11):
        try:
            row = driver.find_element(By.XPATH, f'(//h2)[{scrap}]')
            link = row.find_element(By.XPATH, './a')
            alink = link.getAttribute('href')
            link.click()

            time.sleep(2)  # Consider using WebDriverWait for better performance
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

        except NoSuchElementException:
            print(f'Element not found for scrap {scrap}')
            continue

    driver.quit()

    # Compile messages for Telegram
    messages = []
    for i in range(len(title_list)):
        message_body = (f"مشروع جديد: \nالعنوان: {title_list[i]}\nالوصف: {project_list[i]}"
                        f"\nالسعر: {price_list[i]}\nالمدة: {time_list[i]}\nالرابط: {links_list[i]}")
        messages.append(message_body)

    return messages

# Main function to start the bot and command handlers
async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("scrape", scrape))

    # Start the bot
    await application.start()
    await application.updater.start_polling()

    # Block until the application is stopped
    await application.wait_for_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
