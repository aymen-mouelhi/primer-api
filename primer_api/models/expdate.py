from calendar import monthrange
import datetime


class ExpDate(object):
    """
    An expiration date of a credit card.
    """

    def __init__(self, month, year):
        """
        Attaches the last possible datetime for the given month and year, as
        well as the raw month and year values.
        """
        # Attach month and year
        self.month = month
        self.year = year

        # Get the month's day count
        weekday, day_count = monthrange(year, month)

        # Attach the last possible datetime for the provided month and year
        self.expired_after = datetime.datetime(
            year,
            month,
            day_count,
            23,
            59,
            59,
            999999
        )

    def __repr__(self):
        """
        Returns a typical repr with a simple representation of the exp date.
        """
        return u'<ExpDate expired_after={d}>'.format(
            d=self.expired_after.strftime('%m/%Y')
        )

    @property
    def is_expired(self):
        """
        Returns whether or not the expiration date has passed in American Samoa
        (the last timezone).
        """
        # Get the current datetime in UTC
        utcnow = datetime.datetime.utcnow()

        # Get the datetime minus 11 hours (Samoa is UTC-11)
        samoa_now = utcnow - datetime.timedelta(hours=11)

        # Return whether the exipred after time has passed in American Samoa
        return samoa_now > self.expired_after

    @property
    def mmyyyy(self):
        """
        Returns the expiration date in MM/YYYY format.
        """
        return self.expired_after.strftime('%m/%Y')

    @property
    def mmyy(self):
        """
        Returns the expiration date in MM/YY format (the same as is printed on
        cards.
        """
        return self.expired_after.strftime('%m/%y')

    @property
    def MMYY(self):
        """
        Returns the expiration date in MMYY format
        """
        return self.expired_after.strftime('%m%y')

    @property
    def mm(self):
        """
        Returns the expiration date in MM format.
        """
        return self.expired_after.strftime('%m')

    @property
    def yyyy(self):
        """
        Returns the expiration date in YYYY format.
        """
        return self.expired_after.strftime('%Y')
