import datetime
import logging

# Define logger
logger = logging.getLogger(__name__)

class Chron:

    def __init__(self, hour:int = None, minute:int = None, day:int = None, month:int = None, dow:int = None, year:int = None):
        """Initialices a new Chron object. 
        
        This class generates VERY simple schedule expressions; it works like chrontab in Linux, with the exception that time comparison 
        (i.e. are we in a valid datetime?) has to be done explicitly by calling the method `compare`.

        When an argument is set to None, it's the equivalent of using an asterisk in chrontab. Otherwise, only integers are accepted as valid
        argument values.

        Args:
            hour (int, optional): Hour (24h format) Defaults to None.
            minute (int, optional): Minute. Defaults to None.
            day (int, optional): Day of the month. Defaults to None.
            month (int, optional): Month. Defaults to None.
            dow (int, optional): Day of the week, where 0 == Monday and 6 == Sunday. Defaults to None.
            year (int, optional): Year. Defaults to None.

        Raises:
            ValueError: If any of the arguments is outside a valid range (i.e. 0-23 for hours, 0-59 for minutes, etc).
        """

        # Validate values
        if hour < 0 or hour > 23:
            raise ValueError("Invalid hour value!")
        if minute < 0 or minute > 59:
            raise ValueError("Invalid minute value!")
        if day < 1 or day > 31:
            raise ValueError("Invalid day value!")
        if month < 1 or month > 12:
            raise ValueError("Invalid month value!")
        if dow < 1 or dow > 7:
            raise ValueError("Invalid day of week value!")
        if year < datetime.datetime.now().year:
            raise ValueError("Can't use a past year!")

        # List of valid attributes
        self.chron_attributes = [
            'hour', 'minute', 'day', 'month', 'dow', 'year'
        ]

        # Register values
        self.hour = hour
        self.minute = minute
        self.day = day
        self.month = month
        self.dow = dow
        self.year = year

        # Register values as dict
        self.chron_dict = {
            "hour": self.hour,
            "minute": self.minute,
            "day": self.day,
            "month": self.month,
            "dow": self.dow,
            "year": self.year
        }

    def compare(self, target = datetime.datetime.now(), simple = True):

        # If all values are set to None, then everytime is valid!
        if all([chron_val is None for chron_val in self.chron_dict.values()]):
            if not simple:
                logger.info("All values were set to None in chron object. Taking any datetime value as valid!")
            return True

        # Init a dict to compare values
        chron_values = {}
        
        # Get current date time
        now = datetime.datetime.now()

        # Compare hour
        chron_values["hour"] = True if now.hour() == self.hour or self.hour is None else False
        # Compare minute
        chron_values["minute"] = True if now.minute() == self.minute or self.minute is None else False
        # Compare day
        chron_values["day"] = True if now.day() == self.day or self.day is None else False
        # Compare month
        chron_values["month"] = True if now.month() == self.month or self.month is None else False
        # Compare dow
        chron_values["dow"] = True if now.weekday() == self.dow or self.dow is None else False
        # Compare year
        chron_values["year"] = True if now.year() == self.year or self.year is None else False

        # If all values are set to True, then current time is valid
        if all(chron_values.values()):
            return True
        else:
            return False



