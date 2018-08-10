import copy
import random
import sys
from typing import Callable, Dict, List

from taxi import Taxi
from utils import request2coordinates, travel_time


class Solution:
    def __init__(self, requests: List):
        self.requests = requests
        self.nb_requests = len(requests)
        self.taxis = []

    def build_initial_solution(self, beta: float):
        """
        TODO
        """
        random.shuffle(self.requests)
        self.taxis.append(Taxi(self.requests.pop(0)))
        while len(self.requests) > 0:
            sys.stderr.write("requests pending : %d\r" % len(self.requests))
            # the lower mu is, the better
            mu = self.get_greedy_function(self.taxis[-1], self.requests)
            mu_max = mu[max(mu, key=mu.get)]
            mu_min = mu[min(mu, key=mu.get)]
            RCL_UB = mu_min + beta * (mu_max - mu_min)
            RCL = []
            for request, mu_req in mu.items():
                if mu_req <= RCL_UB:
                    RCL.append(request)
            while len(RCL) > 0:
                request = RCL.pop()
                try:
                    self.taxis[-1].insert(request)
                    self.requests.remove(request)
                    break
                except Exception:
                    continue

            # no requests can be inserted into the route of the last taxi, so we take a new taxi
            if len(RCL) == 0:
                try:
                    self.taxis.append(Taxi(self.requests.pop(0)))
                except IndexError:
                    continue

    def get_greedy_function(self, taxi: Callable, requests: List) -> Dict:
        mu = {}
        for u in requests:  # u is the request to insert in the taxi's route
            delta_source = {}
            delta_destination = {}
            served_requests = []
            for i in range(len(taxi.route)-1):  # we do not care if v is a source point or not
                v = taxi.route[i]
                v_next = taxi.route[i+1]

                v_point, served_requests = request2coordinates(v[1], served_requests)
                v_next_point, served_requests = request2coordinates(v_next[1], served_requests)

                # u source
                # >=
                if v[0] + travel_time(v_point, u.PU_coordinates) >= u.PU_datetime[0]:
                    delta_source[u.id] = travel_time(v_point, u.PU_coordinates) \
                        + travel_time(u.PU_coordinates, v_next_point) - travel_time(v_point, v_next_point)
                # <
                else:
                    delta_source[u.id] = u.PU_datetime[0] - v[0] \
                        + travel_time(u.PU_coordinates, v_next_point) - travel_time(v_point, v_next_point)

                # u destination
                # <=
                if v[0] + travel_time(v_point, u.DO_coordinates) <= u.DO_datetime[1]:
                    delta_destination[u.id] = travel_time(v_point, u.DO_coordinates) \
                        + travel_time(u.DO_coordinates, v_next_point) - travel_time(v_point, v_next_point)
                # >
                else:
                    delta_destination[u.id] = 10000

            # mu[u] is the sum of the 2 minimal delays to insert u in the taxi's route
            mu[u] = min(delta_source, key=lambda x: delta_source.get(x)) \
                + min(delta_destination, key=lambda x: delta_destination.get(x))
        return mu

    @property
    def compute_obj(self) -> int:  # number of shared rides to maximize
        private_rides = [taxi for taxi in self.taxis if len(taxi.route)/2 == 1]
        return self.nb_requests - len(private_rides)

    @property
    def pending_requests(self):
        pending_requests = set()
        for taxi in self.taxis:
            if len(taxi.route) == 2:
                pending_requests.add(taxi.route[0][1])
        return pending_requests

    def local_search(self, max_iter: int=10, nb_swap: int=3):
        """
        TODO
        """
        current_solution = copy.deepcopy(self)
        current_obj = current_solution.compute_obj
        for i in range(max_iter):
            next_solution = current_solution.insert_requests(current_solution.pending_requests, nb_attempts=200)
            next_obj = next_solution.compute_obj
            if next_obj > current_obj:
                current_solution = copy.deepcopy(next_solution)
                current_obj = next_obj
                break
            else:
                for _ in range(nb_swap):
                    current_solution.swap_requests()
        return current_solution, current_obj

    def path_relinking(self, initial_solution):
        


    def insert_requests(self, requests, nb_attempts=10):
        for request in requests:
            for _ in range(nb_attempts):
                taxi = random.sample(self.taxis, 1)
                try:
                    taxi[0].insert(request)
                    break
                except Exception:
                    continue
        return self
        
    def swap_requests(self, nb_attempts: int=100, requests=None):
        """
        Operation used in Santos's both 2013 and 2015 paper.
        Permutation of two requests from different routes.
        """
        if requests:
            try:
                solution = copy.deepcopy(self)
                taxi1, taxi2 = solution.get_taxis_from_requests(requests)
                taxi1.insert(requests[1])
                taxi2.insert(requests[0])
                self = solution
                return
            except Exception:
                print("Failed to swap request %d and request %d" % (requests[0].id, requests[1].id))
                pass
        else:
            for i in range(nb_attempts):
                delays = copy.deepcopy(self.delays)
                taxi_id1, taxi_id2 = random.sample(delays[:10], 2)
                try:
                    solution = copy.deepcopy(self)
                    taxi1 = solution.taxis[taxi_id1[0]]
                    taxi2 = solution.taxis[taxi_id2[0]]
                    request1 = random.sample(taxi1.route, 1)
                    request2 = random.sample(taxi2.route, 1)
                    taxi1.remove(request1[0][1])
                    taxi2.remove(request2[0][1])
                    taxi1.insert(request2[0][1])
                    taxi2.insert(request1[0][1])
                    self = solution
                    return
                except Exception:
                    continue
            print("%d attempts to swap 2 requests without success" % nb_attempts)

    def get_taxis_from_requests(self, requests):
        taxis_serving_requests = []
        for taxi in self.taxis:
            while len(requests) > 0:
                for req in requests:
                    if any(request[1] == req.id for request in taxi.route):
                        taxis_serving_requests.append(self.taxis.index(taxi))
                        requests.remove(req)
        return taxis_serving_requests
    
    @property
    def delays(self):
        delays = []
        for i, taxi in enumerate(self.taxis):
            delays.append((i, taxi.delay))
        delays.sort(key=lambda delay: delay[1], reverse=True)
        return delays

    def swap_points(self, nb_attempts: int=1):
        """
        Operation used only in Santos's 2013 paper.
        Permutation of two consecutive points of the same route.
        """
        for _ in range(nb_attempts):
            try:
                taxi = random.sample(self.taxis, 1)
                pos1, pos2 = random.sample(range(len(taxi)), 2)
                taxi.swap(pos1, pos2)
                return self
            except Exception:
                continue
        raise Exception("%d attempts to swap 2 points of a same request"
                        " without finding any valid route." % nb_attempts)

    def remove_insert_request(self):
        """
        Operation used only in Santos's 2013 paper.
        Removal of some request from some route and attempt to insert,
        in this route, some request that was not served.
        """
