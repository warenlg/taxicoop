import argparse
import copy
import csv
import logging
import pickle
import signal
import sys
import time
from typing import List, Tuple, Dict

from statistics import mean, stdev

from request import Request
from solution import Solution
from utils import travel_time


def setup():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input", type=str,
                        help="Path to the dataset of taxi requests.")
    parser.add_argument("-o", "--output", type=str,
                        help="Path to the output best solution.")
    parser.add_argument("--time-limit", type=int, default=30,
                        help="Maximum time allowed for the algorithm to return a solution.")
    parser.add_argument("--checkpoint-dataset", type=str, required=True,
                        help="Path to the dataset of taxi requests.")
    parser.add_argument("-s", "--size", type=int, default=None,
                        help="Maximum size of the dataset to import.")
    parser.add_argument("-w", "--time-window", type=int, default=15,
                        help="Length of the time windows for both pick up and drop off points.")
    parser.add_argument("--data-saved", action="store_true",
                        help="Load a static instance of the DARP-M with 4298 requests on 30 sec.")
    parser.add_argument("-t", "--timeframe", type=int, default=1000,
                        help="Time length of a static instance (sec).")
    parser.add_argument("--speed", type=int, default=40,
                        help="Constant speed for the taxis: 40km/h in Santos's paper.")
    parser.add_argument("-c", "--capacity", type=int, default=2,
                        help="Seat capacity of each taxi, driver not included.")
    parser.add_argument("--alpha", type=float, default=0.8,
                        help="Customer are paying less than an individual ride times alpha.")
    parser.add_argument("--beta", type=float, default=0.1,
                        help="Size of the Restricted Candidate List (RCL) in the insertion method.")
    parser.add_argument("--limit-RCL", type=float, default=0.2,
                        help="Limit number of the RCL candidates when building the initial greedy solution.")
    parser.add_argument("--num-GRASP", type=int, default=10,
                        help="Maximum number of iterations of the GRASP heuristic.")
    parser.add_argument("--num-local-search", type=int, default=10,
                        help="Maximum number of iterations in the local search.")
    parser.add_argument("--insertion-method", type=str, default="IA", choices=("IA", "IB"),
                        help="Type of insertion method to use."
                             "IA stands for the exhaustive method."
                             "IB stands for the heuristic method.")
    parser.add_argument("--nb-attempts-insert", type=int, default=5,
                        help="Number of times we try to insert a request in the insert_requests() method.")
    parser.add_argument("--nb-swap", type=float, default=0.1,
                        help="Proportion of swap operations to perform in the local search among all requests"
                        "when no improvment has been found in the previous iteration.")
    parser.add_argument("--test-size", type=int, default=200,
                        help="Number of requests to consider to test the algorithm.")
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    return args


def read_dataset(path: str, size: int=None, time_window: int=15) -> List[List[Tuple[float]]]:
    """
    Function to read the input CSV file with the taxi requests.

    param: path: path to the CSV file containg taxi requests, downloaded from
    http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml
    For example 2015-January-Yellow.
    There are no more latitude and longitude coordinates after 2016 but only area zones.
    param: size: an upper bound for the number of rows in the CSV we are reading because
        those CSV files count millions of rows.

    return: a list of taxi requests where one row includes Pick-Up and Drop-Off time windows
        plus Pick-Up and Drop-Off coordinates
    [(PU_datetime - 15min, PU_datetime), (DO_datetime, DO_datetime + 15min),
    (PU_longitude, PU_latitude), (DO_longitude, DO_latitude)]
    """
    log = logging.getLogger("reader")
    fin = open(path, newline="")
    try:
        if not size:  # if no size specified, read the all dataset
            size = sum(1 for _ in csv.reader(fin))
        fin.seek(0)
        reader = csv.reader(fin)
        next(reader)  # to not read the headers
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

            PU_datetime = datetime(row[1])
            PU_coordinates = (float(row[5]), float(row[6]))
            DO_coordinates = (float(row[9]), float(row[10]))
            # we do not use the DO datetime from the dataset because we use distances
            # the distance as the crow flies with constant speed
            DO_datetime = PU_datetime + travel_time(PU_coordinates, DO_coordinates)

            request = []
            request.append((PU_datetime - time_window*60, PU_datetime))
            request.append((DO_datetime, DO_datetime + time_window*60))
            request.append(PU_coordinates)
            request.append(DO_coordinates)

            # filtering
            null_coordinates = PU_coordinates[0] == 0 and DO_coordinates[0] == 0
            coordinates_too_far = DO_datetime - PU_datetime > 12*3600
            same_DO_PU_coordinates = PU_coordinates == DO_coordinates
            if not (null_coordinates and coordinates_too_far and same_DO_PU_coordinates):
                dataset.append(request)

        # sort the requests by Pick-Up datetime
        dataset_sorted = sorted(dataset, key=lambda x: x[0][0])
    finally:
        sys.stderr.write("\n")
        fin.close()
    log.info("Dataset size: %d taxi requests" % len(dataset))
    return dataset_sorted


def initialize_requests(dataset, timeframe: int) -> List:
    log = logging.getLogger("initialize_requests")
    requests = []
    t_0 = dataset[0][0][0]
    log.info("Origin datetime : %d" % t_0)
    for i, req in enumerate(dataset):
        request = Request(req, i+1)
        if request.PU_datetime[0] < t_0 + timeframe:
            requests.append(request)
        else:
            break
    log.info("Timeframe : %d sec" % timeframe)
    log.info("Number of taxi requests : %d" % len(requests))
    return requests

    
def run_GRASP_heuristic(requests, insertion_method, alpha, beta, limit_RCL, num_local_search, nb_attempts_insert, nb_swap):
    nb_requests = len(requests)
    elite_solution = None
    elite_obj = 0
    GRASP_iterations = 0
    time_start = time.clock()
    try:
        while nb_requests - elite_obj is not 0:
            GRASP_iterations += 1
            print()
            print("----- Iteration %d ----- : %0.2f" % (GRASP_iterations, time.clock() - time_start))
            solution = Solution(requests=requests)
            solution.build_initial_solution(insertion_method=insertion_method,
                                            alpha=alpha,
                                            beta=beta,
                                             limit_RCL=limit_RCL)
            solution.check_UB()
            print("1. Local Search :", solution.compute_obj)
            solution.local_search(insertion_method=insertion_method,
                                  alpha=alpha,
                                  max_iter=num_local_search,
                                  nb_attempts_insert=nb_attempts_insert,
                                  nb_swap=nb_swap)

            solution.check_UB()
            if elite_solution:
                print("2. Path Relinking :", solution.compute_obj)
                output_solution = solution.path_relinking(initial_solution=elite_solution,
                                                          insertion_method=insertion_method,
                                                          alpha=alpha,
                                                          nb_attempts_insert=nb_attempts_insert)
                solution = output_solution
                solution.check_UB()
                print("3. Second Local Search :", solution.compute_obj)
                solution.local_search(insertion_method=insertion_method,
                                      alpha=alpha,
                                      max_iter=num_local_search,
                                      nb_attempts_insert=nb_attempts_insert,
                                      nb_swap=nb_swap)
                solution.check_UB()
                if solution.compute_obj > elite_obj:
                    elite_solution = copy.deepcopy(solution)
            else:
                elite_solution = copy.deepcopy(solution)
            print()
            print("Elite obj :", elite_solution.compute_obj)
    
    except (RuntimeError, StopIteration) as r:
        if solution.compute_obj > elite_solution.compute_obj:
            elite_solution = copy.deepcopy(solution)
        pass

    stats = {}
    time_elapsed = time.clock() - time_start
    stats["time"] = time_elapsed
    stats["GRASP iterations"] = GRASP_iterations
    return elite_solution, stats


def test_solution(solution):
    print()
    print("---------------------------------------------------------")
    print("            Tests on the best solution found                       ")
    print("---------------------------------------------------------")
    print()
    try:
        solution.check_requests_served_once()
        solution.visualize()
        solution.check_time_windows()
        print("Fianl best solution valid")
    except ValueError as e:
        print(e)


def print_stats(solution, stats: Dict):
    print()
    print("---------------------------------------------------------")
    print("                     Final stats                         ")
    print("---------------------------------------------------------")
    print()
    nb_requests = solution.nb_requests
    obj = solution.compute_obj
    all_individual_delays, all_individual_delays_per, all_individual_savings_per, all_individual_earlier_starts, all_individual_earlier_starts_per = solution.all_individual_stats
    print("Number of requests :", nb_requests)
    print("Number of GRASP iterations :", stats["GRASP iterations"])
    print("Best obj :", obj)
    print("Percentage of pooling : %0.1f %%" % (obj*100 / nb_requests))

    print()
    print("Average delay for the customers accepting the pooling : %0.1f sec (+%0.1f %%)"
          % (mean(all_individual_delays), mean(all_individual_delays_per)))
    print("Standard Deviation of the delay : %0.1f sec" % (stdev(all_individual_delays)))
    print("Maximum delay : %0.1f sec (+%0.1f %%)" % (max(all_individual_delays), max(all_individual_delays_per)))
    print("Minimum delay : %0.1f sec (+%0.1f %%)" % (min(all_individual_delays), min(all_individual_delays_per)))

    print()
    print("Average price saving for the customers accepting the pooling : -%0.1f %%"
          % (mean(all_individual_savings_per)))
    print("Maximum price saving : -%0.1f %%" % (max(all_individual_savings_per)))
    print("Minimum price saving : -%0.1f %%" % (min(all_individual_savings_per)))

    print()
    print("Average time advance the clients are pickep up with : %0.1f sec (+%d %%)"
          % (mean(all_individual_earlier_starts), mean(all_individual_earlier_starts_per)))
    print("Standard Deviation of the pick up time advance : %d sec" % (stdev(all_individual_earlier_starts)))
    print("Maximum pick up time advance : %d sec (+%d %%)" % (max(all_individual_earlier_starts), max(all_individual_earlier_starts_per)))
    print("Minimum pick up time advance : %d sec (+%d %%)" % (min(all_individual_earlier_starts), min(all_individual_earlier_starts_per)))

    print()
    print("Computation time : %d sec" % (round(stats["time"])))
    print("Average computation time by iteration : %0.2f sec" % (round(stats["time"], 2) / stats["GRASP iterations"]))


def main():
    args = setup()
    if args.data_saved:
        with open(args.checkpoint_dataset, "rb") as f:
            requests = pickle.load(f)[:args.test_size]
    else:
        dataset = read_dataset(args.input, args.size, args.time_window)
        requests = initialize_requests(dataset, timeframe=args.timeframe)[:args.test_size]
        with open(args.checkpoint_dataset, "wb") as f:
            pickle.dump(requests, f)
    nb_requests = len(requests)

    def handler(signum, frame):
        raise RuntimeError("End of the %d sec" % (args.time_limit))

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(args.time_limit)

    print("Starting GRASP iterations...")
    elite_solution, stats = run_GRASP_heuristic(requests=requests,
                                                insertion_method=args.insertion_method,
                                                alpha=args.alpha,
                                                beta=args.beta,
                                                limit_RCL=args.limit_RCL,
                                                num_local_search=args.num_local_search,
                                                nb_attempts_insert=args.nb_attempts_insert,
                                                nb_swap=args.nb_swap)
    test_solution(elite_solution)
    print_stats(elite_solution, stats)


if __name__ == "__main__":
    sys.exit(main())
