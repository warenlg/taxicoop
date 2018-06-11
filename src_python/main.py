import argparse
import csv
import logging
import os
import sys

import numpy


def setup():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", required=True,
                        help="Path to the dataset of taxi requests.")
    parser.add_argument("-s", "--size", type=int, default=None,
                        help="Maximum size of the dataset to import.")
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    return args


def read_dataset(path: str, size: int=None) -> numpy.ndarray:
    """
    Function to read the input CSV file with the taxi requests.

    param: path to the CSV file containg taxi requests, downloaded from
    http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml
    For example 2015-January-Yellow.
    There are no more latitude and longitude coordinates after 2016 but only area zones.
    param: size is an upper bound for the number of rows in the CSV we are reading because
    those CSV files count millions of rows.

    return: a numpy array of taxi requests where one row is
    [PU_datetime, DO_datetime, PU_longitude, PU_latitude, DO_longitude, DO_latitude]
    """
    log = logging.getLogger("reader")
    fin = open(path, newline="")
    try:
        if not size: # if no size specified, read the all dataset
            size = sum(1 for _ in csv.reader(fin))
        fin.seek(0)
        reader = csv.reader(fin)
        next(reader) # to not read the headers
        requests = numpy.zeros((size, 6), dtype=numpy.float32)
        for i, row in enumerate(reader):
            if i % 1000 == 0:
                sys.stderr.write("%d\r" % i)
            if i >= size:
                break
            for j, val in enumerate(row):
                if j in (1, 2):
                    datetime = val.split()
                    timestamp = datetime[1].split(":")
                    timestamp = [int(x) for x in timestamp]
                    hour, minutes, seconds = tuple(timestamp)
                    time_absolute = hour*3600 + minutes*60 + seconds
                    requests[i][j-1] = time_absolute
                elif j in (5, 6):
                    requests[i][j-3] = float(val)
                elif j in (9, 10):
                    requests[i][j-5] = float(val)
    finally:
        sys.stderr.write("\n")
        fin.close()
    return requests


def main():
    args = setup()
    requests = read_dataset(args.input, args.size)  


if __name__ == "__main__":
    sys.exit(main())
