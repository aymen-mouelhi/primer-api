import re
from .expdate import ExpDate


class CreditCard(object):
    """
    A credit card that may be valid or invalid.
    """
    # A regexp for matching non-digit values
    non_digit_regexp = re.compile(r'\D')

    def __init__(self, number, month, year):
        """
        Attaches the provided card data and holder to the card after removing
        non-digits from the provided number.
        """
        self.number = self.non_digit_regexp.sub('', number)
        self.exp_date = ExpDate(month, year)

    def __repr__(self):
        """
        Returns a typical repr with a simple representation of the card
        number and the exp date.
        """
        return u'<CreditCard number={n}, exp_date={e}>'.format(
            n=self.number,
            e=self.exp_date.mmyyyy
        )

    @property
    def is_expired(self):
        """
        Returns whether or not the card is expired.
        """
        return self.exp_date.is_expired

    @property
    def is_valid(self):
        """
        Returns whether or not the card is a valid card for making payments.
        """
        return not self.is_expired and self.is_mod10_valid

    @property
    def is_mod10_valid(self):
        """
        Returns whether or not the card's number validates against the mod10
        algorithm (Luhn algorithm), automatically returning False on an empty
        value.
        """
        # Check for empty string
        if not self.number:
            return False

        # Run mod10 on the number
        dub, tot = 0, 0
        for i in range(len(self.number) - 1, -1, -1):
            for c in str((dub + 1) * int(self.number[i])):
                tot += int(c)
            dub = (dub + 1) % 2

        return (tot % 10) == 0
