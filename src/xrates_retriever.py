import os
import re
import sys
import time

from datetime import datetime
from forex_python.converter import CurrencyRates
from pathlib import Path


def validate_date(date_text):
    """Validates that the date is in ISO 8601 format: YYYY-MM-DD"""
    try:
        if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
            return False
        return True
    except ValueError:
        return False


def get_rate(input_date, exchange_currency, base_currency):
    """ Returs the exchange rate of a currency on a particular day.

    The date should be in ISO 8601 format: YYYY-MM-DD
    If the date is invalid the exchange range returned is an empty string.
    """

    if not validate_date(input_date):
        return ""

    date_array = input_date.split("-")

    year   = int(date_array[0])
    month  = int(date_array[1])
    day    = int(date_array[2])
    hour   = 12
    minute = 0
    second = 0
    millys = 0

    date_object = datetime(year, month, day, hour, minute, second, millys)

    return CurrencyRates().get_rate(exchange_currency, base_currency, date_object)


def get_timestamp():
    """Gets a timestamp for filenaming with format as: 20191231_235959"""
    return time.strftime("%Y%m%d_%H%M%S")


def get_currency_codes():
    """Returns a list with the supported currency codes"""
    return [x for x in CurrencyRates().get_rates("USD")]


def print_currency_pair_help():
    """Prints out the relevant help for the currency pair code"""

    print(f"The currency codes must have 3 capital letters as per ISO 4217")
    print(f"for example: EUR\n")
    print(f"The header line of the input file must be the currency pair as:")
    print(f"<Exchange currency code><Base currency code>\n")
    print(f"for example: USDEUR\n")


def retrieve_xrates(input_file):
    """ The program initially validates the input file
    for its existence and size and then checks that
    the header line contains a valid currency pair.

    Then check the currency codes of each of the exchange
    and base currnecies based on the format as per the ISO 4217.

    The currency pair should be like:
        <exchange currency code><base currency code>
    for example:
        USDEUR

    The program attempts to retrive the exchange rates
    using the following library:

        forex_python
        https://github.com/MicroPyramid/forex-python

    Invalid dates according to the ISO 8601 format (YYYY-MM-DD),
    will be redirected to an "errors" file with "na" exchange rate.

    The output file will have the currency pair on the header line
    and then date line such as:
        <date>,<exchange rate>
    for example:
        2019-31-12,0.9581297308

    """

    program_title="x-rates retrieval program"

    print(f"{program_title}\n")

    # Checks if input file exists.
    if not os.path.isfile(input_file):
        print(f"Input file not found: {input_file}")
        sys.exit(1)

    # Checks if input file has size.
    if not os.path.getsize(input_file) > 0:
        print(f"Input file is empty: {input_file}")
        sys.exit(2)
    
    # Locates the directory that contains the input file
    input_dir = Path(os.path.dirname(os.path.realpath(input_file)))
        
    print(f"Input directory: {input_dir}")
    print(f"Input filename: {input_file}")
    
    # Stores the input file into a list.
    with open(input_file) as f:
        lines = [line.rstrip() for line in f]

    # Splits the lines list into the
    # header line which is the currency pair
    # and the dates which are teh rest of them.
    currency_pair, dates = lines[0], lines[1:]

    # Validates the legth of the currency pair.
    # The currency code length is 3 as per the ISO 4217.
    currency_code_length = 3
    if len(currency_pair) != currency_code_length * 2:
        print(f"Invalid currency pair: {currency_pair}\n")
        print_currency_pair_help()
        sys.exit(3)

    # Splits the exchange pair to exchange and base currencies.
    exchange_currency = currency_pair[:currency_code_length]
    base_currency = currency_pair[currency_code_length:]

    # Checks if the currency code is supported thus valis.
    for currency in [exchange_currency, base_currency]:
        if not currency in get_currency_codes():
            print(f"Currency code is not supported: {currency}\n")
            print_currency_pair_help()
            sys.exit(4)

    print(f"")
    print(f"Exchange currency: {exchange_currency}")
    print(f"Base currency    : {base_currency}")
    print(f"Dates count      : {str(len(dates))}")
    print(f"")

    print(f"Retrival has started. This might take a while...\n")
    start = time.time()

    # Constructs the output and error file names.
    timestamp = get_timestamp()
    output_filename = f"output_{timestamp}.txt"
    errors_filename = f"errors_{timestamp}.txt"
    
    # Construct the output and error file paths.
    output_dir = input_dir
    output_path = Path(output_dir / output_filename).resolve()
    errors_path = Path(output_dir / errors_filename).resolve()

    # Opens the output and error files.
    output_file = open(output_path, 'w')
    errors_file = open(errors_path, 'w')

    # Writes currency pair on the header line.
    output_file.write(currency_pair + "\n")
    errors_file.write(currency_pair + "\n")

    # Writes the date and the exchange rate on each line.
    # The output field separator is comma.
    output_seaparator = ","

    valid_dates = 0
    invalid_dates = 0
    for date in dates:
        rate = get_rate(date, exchange_currency, base_currency)

        if rate != "":
            output_file.write(date + output_seaparator + str(rate) + "\n")
            valid_dates += 1
        else:
            errors_file.write(date + output_seaparator +    "na"   + "\n")
            invalid_dates += 1

    # Closes the output and errors files.
    output_file.close()
    errors_file.close()

    print(f"Retrieval has completed in: {round(time.time() - start, 0)} sec\n")

    print(f"Valid dates  : {valid_dates}")
    print(f"Invalid dates: {invalid_dates}\n")

    
    print(f"Output directory: {output_dir}")
    print(f"Output file: {output_filename}")

    # If there are invalid dates, reports the errors file.
    # Otherwise, cleans-up the errors file.
    if invalid_dates > 0:
        print(f"Errors file: {errors_filename}")
    else:
        os.remove(output_path)


def main():
    
    # Argument handlind. 
    # Setting default input file
    if len(sys.argv) - 1 == 1:
        input_file = sys.argv[1]
    else:
        input_file = "../data/input.txt"

    retrieve_xrates(input_file)


if __name__== "__main__":
    main()
