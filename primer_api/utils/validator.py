import re


def sum_digits(digit):
    if digit < 10:
        return digit
    else:
        sum = (digit % 10) + (digit // 10)
        return sum


def validate(cc_num):
    # reverse the credit card number
    cc_num = cc_num[::-1]
    # convert to integer list
    cc_num = [int(x) for x in cc_num]
    # double every second digit
    doubled_second_digit_list = list()
    digits = list(enumerate(cc_num, start=1))
    for index, digit in digits:
        if index % 2 == 0:
            doubled_second_digit_list.append(digit * 2)
        else:
            doubled_second_digit_list.append(digit)

    # add the digits if any number is more than 9
    doubled_second_digit_list = [sum_digits(x) for x in doubled_second_digit_list]
    # sum all digits
    sum_of_digits = sum(doubled_second_digit_list)
    # return True or False
    return sum_of_digits % 10 == 0


def extract_month_year(expiration_date):
    result = re.findall(r'(\d{2})/(\d{4})', expiration_date)
    if len(result) > 0:
        result = ','.join(result[0])
        result = list(int(i) for i in result.split(','))
        return result[0], result[1]
    else:
        # try with 2 digits for the year
        result = re.findall(r'(\d{2})/(\d{2})', expiration_date)
        if len(result) > 0:
            result = ','.join(result[0])
            result = list(int(i) for i in result.split(','))
            result[1] += 2000
            return result[0], result[1]
    return None, None

def validate_amount(amount):
    r = re.compile(r"^(?=.*?\d)\d*[.,]?\d*$")
    return not (r.match(amount) is None)
