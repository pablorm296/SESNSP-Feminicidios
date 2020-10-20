from SnapBot.Chron import Chron
from SnapBot.Secrets import *

import telegram
import datetime
import logging
import subprocess
import requests
import os

# Define logger
logger = logging.getLogger(__name__)

class SnapBot:

    def __init__(self, targetURL:str, savePath:str, hour:int = None, minute:int = None, day:int = None, month:int = None, dow:str = None, year:int = None):
        # Validate save path
        if os.path.isdir(savePath):
            self.savePath = savePath
        else:
            raise ValueError("The specified save directory does not exist!")

        # Build chron object
        logging.info("Initializing chron expression...")
        self.Chron = Chron(hour = hour, minute = minute, day = day, month = month, dow = dow, year = year)

        # Init Telegram Bot
        logging.info("Initializing telegram bot...")
        self.TelegramBot = telegram.Bot(token = TELEGRAM_BOT_TOKEN)

        # Register target group chat
        logging.info("Registering chat ID...")
        self.TelegramChatId = TELEGRAM_BOT_CHAT_ID
        
        # Register target url
        self.targetURL = targetURL

        # Send test message
        logging.info("Sending test message...")
        self.TelegramBot.send_message(self.TelegramChatId, "Hi! Im a the SESNSP Snap Bot. I just wake up, and briefly I will make a snap shot of the target entry at the SESNSP web site!")

    def sendTelegramAlert(self, msg:str):
        pass

    def compareChronExpression(self):
        # Compare chron expression with current datetime
        return self.Chron.compare()

    def getFullPage(self, savePath:str = None, force:bool = False):
        # If savePath is not defined, use class path
        if savePath is None:
            savePath = self.savePath

        # Compare chron date
        if not force and not self.compareChronExpression():
            error_msg = "Attempted to run bot routine outside a valid timedate!"
            logger.error(error_msg)
            raise Exception(error_msg)

        # Create new directory in save path
        # Define directory name
        dirName = "FullPage_{0}".format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S%f"))
        # Define full dir name
        fullDirName = "{0}/{1}".format(savePath, dirName)

        # Create dir
        logger.info("Creating directory ({0})...".format(fullDirName))
        os.mkdir(fullDirName)

        # Check if page is online
        logger.info("Testing target URL ({0})".format(self.targetURL))
        test_response = requests.get(self.targetURL)

        if test_response.status_code >= 300:
            logger.warning("The target URL responded with a {0} status code! Please make a manual check of the page.".format(test_response.status_code))

        # Use wget to make copy of page
        logger.info("Running wget from suprocess...")
        # -E adjust extension (Urls not ending in .htm*)
        # -k convert links (Change all links to relative local links)
        # -K backup (When converting a file, back up the original version with a .orig suffix)
        # -p page requisites (Download all the original files needed to display the downloaded page)
        # -H span hosts
        subprocess_return = subprocess.call(['wget', '-E', '-H','-k', '-K', '-p', self.targetURL])

    def getDocument(self, savePath:str = None, force:bool = False):
        # If savePath is not defined, use class path
        if savePath is None:
            savePath = self.savePath

        # Compare chron date
        if not force and not self.compareChronExpression():
            error_msg = "Attempted to run bot routine outside a valid timedate!"
            logger.error(error_msg)
            raise Exception(error_msg)