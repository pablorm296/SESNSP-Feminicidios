from SnapBot.Chron import Chron
from SnapBot.Secrets import *
from SnapBot.Google.Drive import download_document, get_document_id

from lxml import etree
from bs4 import BeautifulSoup
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
        # Init Telegram Bot
        logging.info("Initializing telegram bot...")
        self.TelegramBot = telegram.Bot(token = TELEGRAM_BOT_TOKEN)

        # Register target group chat
        logging.info("Registering chat ID...")
        self.TelegramChatId = TELEGRAM_BOT_CHAT_ID

        # Send test message
        logging.info("Sending test message...")
        self.sendTelegramAlert("Hi! I'm the SESNSP Snap Bot 🤖. I just wake up and briefly I will make a snapshot of the target entry at the SESNSP web site!")
        
        # Validate save path
        logging.info("Validating path...")
        if os.path.isdir(savePath):
            self.savePath = savePath
        else:
            # Define error message
            error_msg = "The specified path (<code>{0}</code>) to save the snapshot does not exist (or I can't access it 😖)! Please contact my administrator.".format(savePath)
            # Log error
            logger.error(error_msg)
            # Send error message to telegram chat
            self.sendTelegramAlert("🛑 Something went wrong! {0}".format(error_msg))
            # Raise error
            raise OSError(error_msg)

        # Build chron object
        logging.info("Initializing chron expression...")
        self.Chron = Chron(hour = hour, minute = minute, day = day, month = month, dow = dow, year = year)
                
        # Register target url
        logging.info("Registering target URL...")
        self.targetURL = targetURL

        # Register server IP
        logging.info("Registering server IP...")
        self.serverURL = SERVER_IP

        # Register server IP
        logging.info("Registering server public path...")
        self.serverPublicPath = SERVER_PUBLIC_PATH

    def sendTelegramAlert(self, msg:str):

        # Send message
        self.TelegramBot.send_message(self.TelegramChatId, msg, parse_mode = "HTML")

    def compareChronExpression(self):
        # Compare chron expression with current datetime
        return self.Chron.compare()

    def getFullPage(self, savePath:str = None, force:bool = False):
        # If savePath is not defined, use class path
        if savePath is None:
            savePath = self.savePath

        # Compare chron date
        if not force and not self.compareChronExpression():
            # Define error message
            error_msg = "I was woken up outside a valid schedule expression 😞!"
            # Log error
            logger.error(error_msg)
            # Send error message to telegram chat
            self.sendTelegramAlert("🛑 Something went wrong! {0}".format(error_msg))
            raise Exception(error_msg)

        # Create new directory in save path
        # Define directory name
        dirName = "FullPage_{0}".format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M-%S-%f"))
        # Define full dir name
        fullDirName = "{0}/{1}".format(savePath, dirName)

        # Create dir
        logger.info("Creating directory ({0})...".format(fullDirName))
        os.mkdir(fullDirName)

        # Check if page is online
        logger.info("Testing target URL ({0})...".format(self.targetURL))
        test_response = requests.get(self.targetURL)

        if test_response.status_code >= 300:
            error_msg = "The target URL responded with an unsuccessful status code (<code>{0}</code>). Please make a manual check of the page.".format(test_response.status_code)
            # Log error
            logger.error(error_msg)
            # Send telegram message
            self.sendTelegramAlert("🛑 Something went wrong! {0}".format(error_msg))
            # Raise
            raise OSError(error_msg)
        else:
            logger.info("The target URL appears to be ok!")

        # Use wget to make copy of page
        logger.info("Running wget from suprocess...")
        # -E adjust extension (Urls not ending in .htm*)
        # -k convert links (Change all links to relative local links)
        # -K backup (When converting a file, back up the original version with a .orig suffix)
        # -p page requisites (Download all the original files needed to display the downloaded page)
        # -e robots=off
        # -nv Simple output
        # -P dir suffix (output to specified directory)
        # -H span hosts
        subprocess_return = subprocess.run('wget -E -H -k -K -e robots=off -nv -p -P {0} {1}'.format(fullDirName, self.targetURL), capture_output = True, shell = True)

        # Check return status from subprocess
        if subprocess_return.returncode != 0:
            # Define error message
            error_msg = "<code>wget</code> returned a non zero status code (<code>{0}</code>)! Sometimes this happens when there are minor network failures. The captured output from stderr was: <pre>{1}</pre> Please contact my administrator.".format(subprocess_return.returncode, subprocess_return.stderr.decode('utf-8'))
            # Send telegram alert
            self.sendTelegramAlert("⚠ Something didn't add up! {0}".format(error_msg))
            # Log error
            logger.warning(error_msg)

        logger.info("wget finished with a '{0}' exit status".format(subprocess_return.returncode))

        # Get lines of stderr (IDK why wget sends everything to stderr)
        subprocess_lines = subprocess_return.stderr.decode("utf-8").splitlines()
        subprocess_last_line = subprocess_lines[-1]
        
        # Send last line of std
        self.sendTelegramAlert("🥳 I successfully made a snapshot of the target entry at the SESNSP website. <code>wget</code> says: <pre>{0}</pre>".format(subprocess_last_line))

        # Zip it
        logger.info("Compressing downloaded file...")
        subprocess_return = subprocess.run('zip -r {0}.zip {0}'.format(fullDirName), capture_output = True, shell = True)

        # Check result
        if subprocess_return.returncode != 0:
            # Define error message
            error_msg = "I failed to zip the downloaded snapshot ☹. The captured stderr says: <pre>{0}</pre>".format(subprocess_return.stderr.decode('utf-8'))
            # Send telegram message
            self.sendTelegramAlert("🛑 Something went wrong! {0}".format(error_msg))
            # Raise
            raise OSError(error_msg)

        # Get md5sum
        logger.info("Getting md5 hash sum...")
        subprocess_return = subprocess.run('md5sum {0}.zip'.format(fullDirName), capture_output = True, shell = True)

        # Check result
        if subprocess_return.returncode != 0:
            # Define error message
            error_msg = "I failed to get the MD5 sum of the downloaded snapshot ☹. The captured stderr says: <pre>{0}</pre>".format(subprocess_return.stderr.decode('utf-8'))
            # Send telegram message
            self.sendTelegramAlert("🛑 Something went wrong! {0}".format(error_msg))
            # Raise
            raise OSError(error_msg)

        md5sum = subprocess_return.stdout.decode('utf-8').split(" ")[0]

        # Send md5sum via Telegram
        self.sendTelegramAlert("MD5 hash sum of the compressed snapshot: <code>{0}</code>".format(md5sum))

        # Make a copy of the file into the public server path
        logger.info("Making a copy into the public directory of the server...")
        subprocess_return = subprocess.run('cp {0}.zip {1}FullPage/{2}.zip'.format(fullDirName, self.serverPublicPath, dirName), capture_output = True, shell = True)

        # Check result
        if subprocess_return.returncode != 0:
            # Define error message
            error_msg = "I failed to make a public copy of the snapshot ☹. The captured stderr says: <pre>{0}</pre>".format(subprocess_return.stderr.decode('utf-8'))
            # Send telegram message
            self.sendTelegramAlert("🛑 Something went wrong! {0}".format(error_msg))
            # Raise
            raise OSError(error_msg)

        # Create link
        fullPage_dir_link = "http://{0}/FullPage/{1}.zip".format(self.serverURL, dirName)

        # Send link
        self.sendTelegramAlert('😌 You can download the compressed snapshot <a href="{0}">here</a>'.format(fullPage_dir_link))

    def getDocument(self, savePath:str = None, force:bool = False):
        # If savePath is not defined, use class path
        if savePath is None:
            savePath = self.savePath

        # Compare chron date
        if not force and not self.compareChronExpression():
            error_msg = "Attempted to run bot routine outside a valid timedate!"
            logger.error(error_msg)
            raise Exception(error_msg)

        # Compare chron date
        if not force and not self.compareChronExpression():
            # Define error message
            error_msg = "I was woken up outside a valid schedule expression 😞!"
            # Log error
            logger.error(error_msg)
            # Send error message to telegram chat
            self.sendTelegramAlert("🛑 Something went wrong! {0}".format(error_msg))
            raise Exception(error_msg)

        # Check if page is online
        logger.info("Testing target URL ({0})...".format(self.targetURL))
        test_response = requests.get(self.targetURL)

        if test_response.status_code >= 300:
            error_msg = "The target URL responded with an unsuccessful status code (<code>{0}</code>). Please make a manual check of the page.".format(test_response.status_code)
            # Log error
            logger.error(error_msg)
            # Send telegram message
            self.sendTelegramAlert("🛑 Something went wrong! {0}".format(error_msg))
            # Raise
            raise Exception(error_msg)
        else:
            logger.info("The target URL appears to be ok!")

        # If response was ok, parse response with BeautifulSoup
        logger.info("Parsing response...")
        parsed_response = BeautifulSoup(test_response.text, 'html.parser')
        # Create dom with etree
        dom = etree.HTML(str(parsed_response))

        # Search by xpath
        logger.info("Looking for link via xpath...")
        xpath_result = dom.xpath('/html/body/main/div/div[1]/div[4]/div/p[2]/a/@href')

        # Predefine a regex_result
        regex_result = None

        # Check if xpath returned something
        if len(xpath_result) < 1:
            xpath_result = None
            # Log warning
            logger.warning("Didn't get a valid href via xpath. Trying regex...")
            # Send alert
            self.sendTelegramAlert("😧 I couldn't find a valid link to the target document using the expected Xpath. I will try suing some regex magic...")

            # Search using regex
            regex_result = dom.xpath('.//a[contains(text(),"Consulta la información")]/@href')

            if len(regex_result) < 1:
                regex_result = None
        
        # Check both results
        if regex_result is None and xpath_result is None:
            # Define error msg
            error_msg = "I failed to get the document link (both by using XPATH and regex). Maybe the page was modified? Pleas contact my administrator."
            # Log error
            logger.error(error_msg)
            # Send alert
            self.sendTelegramAlert("🛑 Something went wrong! {0}".format(error_msg))
            # Raise
            raise Exception(error_msg)
        
        # Get href
        href = xpath_result[0] if xpath_result is not None else regex_result[0]
        
        # Send link to telegram
        self.sendTelegramAlert('😌 It appears that the document was shared via <a href="{0}">this link</a>.'.format(href))

        # Now, get the document id
        logger.info("Getting document ID...")
        document_id = get_document_id(href)

        # Check document id
        if len(document_id) < 1 or len(document_id) > 1:
            # Define error msg
            error_msg = "I failed to get the document ID. Maybe it's no longer shared via Google Drive? Please contact my administrator."
            # Log error
            logger.error(error_msg)
            # Send alert
            self.sendTelegramAlert("🛑 Something went wrong! {0}".format(error_msg))
            # Raise
            raise Exception(error_msg)

        # Define document name
        docName = "Document_{0}.pdf".format(datetime.datetime.now().strftime("%Y-%m-%d-%H%M-%S-%f"))
        # Define full dir name
        fullDocName = "{0}/{1}".format(savePath, docName)

        # Download document
        logger.info("Downloading document...")
        try:
            download_document(document_id, fullDocName)
        except Exception as e:
            # Define error msg
            error_msg = "I failed to download the document ID. The raised exception says: <pre>{0}</pre>".format(str(e))
            # Log error
            logger.error(error_msg)
            # Send alert
            self.sendTelegramAlert("🛑 Something went wrong! {0}".format(error_msg))
            # Raise
            raise Exception(error_msg)

        # Send alert
        self.sendTelegramAlert("🥳 I successfully made a snapshot of the target document at the SESNSP website.")

        # Get md5sum
        logger.info("Getting md5 hash sum...")
        subprocess_return = subprocess.run('md5sum {0}'.format(fullDocName), capture_output = True, shell = True)

        # Check result
        if subprocess_return.returncode != 0:
            # Define error message
            error_msg = "I failed to get the MD5 sum of the downloaded document ☹. The captured stderr says: <pre>{0}</pre>".format(subprocess_return.stderr.decode('utf-8'))
            # Send telegram message
            self.sendTelegramAlert("🛑 Something went wrong! {0}".format(error_msg))
            # Raise
            raise OSError(error_msg)

        md5sum = subprocess_return.stdout.decode('utf-8').split(" ")[0]

        # Send md5sum via Telegram
        self.sendTelegramAlert("MD5 hash sum of the downloaded document: <code>{0}</code>".format(md5sum))

        # Make a copy of the file into the public server path
        logger.info("Making a copy into the public directory of the server...")
        subprocess_return = subprocess.run('cp {0} {1}Documents/{2}'.format(fullDocName, self.serverPublicPath, docName), capture_output = True, shell = True)

        # Check result
        if subprocess_return.returncode != 0:
            # Define error message
            error_msg = "I failed to make a public copy of the downloaded document ☹. The captured stderr says: <pre>{0}</pre>".format(subprocess_return.stderr.decode('utf-8'))
            # Send telegram message
            self.sendTelegramAlert("🛑 Something went wrong! {0}".format(error_msg))
            # Raise
            raise OSError(error_msg)

        # Create link
        document_link = "http://{0}/FullPage/{1}".format(self.serverURL, docName)

        # Send link
        self.sendTelegramAlert('😌 You can download the downloaded document <a href="{0}">here</a>'.format(document_link))
        