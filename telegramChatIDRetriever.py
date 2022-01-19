import requests
import os
from dotenv import load_dotenv
import json
load_dotenv()

# Retrieves Telegram chat ID. Set Telegram bot token in .env first.

telegramTokenList = os.environ.get("telegramBotTokens").split(",")

for telegramToken in telegramTokenList:
	responseContents = json.loads(requests.get(f'https://api.telegram.org/bot{telegramToken}/getUpdates').text)

	try:
		if 'error_code' in responseContents:
			print("Set telegramBotToken in your .env file first.")
		else:
			print(f"Telegram chat ID of {telegramToken} is: " + str(responseContents['result'][0]['message']['chat']['id']))
	except IndexError:
		print(f"Send any message to {telegramToken} and run again.")