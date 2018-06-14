import argparse
import csv
import logging
import os
import sys
from typing import Tuple, List

import numpy


def setup():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", required=True,
                        help="Path to the dataset of taxi requests.")
    parser.add_argument("-s", "--size", type=int, default=None,
                        help="Maximum size of the dataset to import.")
    parser.add_argument("-v", "--speed", type=int, default=40,
                        help="Constant speed for the taxis: 40km/h in Santos's paper.")
    parser.add_argument("-c", "--capacity", type=int, default=2,
                        help="Seat capacity of each taxi, driver not included.")
    parser.add_argument("--alpha", type=float, default=1,
                        help="Customer are paying less than an individual ride times alpha.")
    parser.add_argument("--max-iter", type=int, default=100,
                        help="Maximum number of iterations in the algorithm.")
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    return args


def read_dataset(path: str, size: int=None, time_window: int=15) -> List:
    """
    Function to read the input CSV file with the taxi requests.

    param: path to the CSV file containg taxi requests, downloaded from
    http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml
    For example 2015-January-Yellow.
    There are no more latitude and longitude coordinates after 2016 but only area zones.
    param: size is an upper bound for the number of rows in the CSV we are reading because
        those CSV files count millions of rows.

    return: a list of taxi requests where one row includes Pick-Up and Drop-Off time windows
        plus Pick-Up and Drop-Off coordinates
    [(PU_datetime - 15min, PU_datetime), (DO_datetime, DO_datetime + 15min),
    (PU_longitude, PU_latitude), (DO_longitude, DO_latitude)]
    """
    log = logging.getLogger("reader")
    fin = open(path, newline="")
    try:
        if not size: # if no size specified, read the all dataset
            size = sum(1 for _ in csv.reader(fin))
        fin.seek(0)
        reader = csv.reader(fin)
        next(reader) # to not read the headers
        dataset = []

        def datetime(val: str) -> int:
            datetime = val.split()
            timestamp = datetime[1].split(":")
            timestamp = [int(x) for x in timestamp]
            hour, minutes, seconds = tuple(timestamp)
            time_absolute = hour*3600 + minutes*60 + seconds
            return time_absolute

        for i, row in enumerate(reader):
            if i % 1000 == 0:
                sys.stderr.write("%d\r" % i)
            if i >= size:
                break
            request = []
            request.append((datetime(row[1]) - time_window*60, datetime(row[1])))
            request.append((datetime(row[2]), datetime(row[2]) + time_window*60))
            request.append((float(row[5]), float(row[6])))
            request.append((float(row[9]), float(row[10])))
            # some requests are corrupted, we don't add them to the dataset
            if request[0][1] < request[1][0]:
                dataset.append(request)
    finally:
        sys.stderr.write("\n")
        fin.close()
    return dataset, len(dataset)


def main():
    args = setup()
    dataset, nb_requests = read_dataset(args.input, args.size)
    print("len_dataset :", nb_requests)


if __name__ == "__main__":
    sys.exit(main())
