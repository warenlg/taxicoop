from collections import defaultdict
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
            #sys.stderr.write("requests pending : %d\r" % len(self.requests))
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
        pending_requests = {}
        for taxi in self.taxis:
            if len(taxi.route) == 2:
                pending_requests[taxi.route[0][1].id] = taxi.route[0][1]
        return pending_requests

    def local_search(self, max_iter: int=10, nb_swap: int=3):
        """
        TODO
        """
        current_solution = copy.deepcopy(self)
        current_obj = current_solution.compute_obj
        for i in range(max_iter):
            print("i :", i)
            next_solution = current_solution.insert_requests(current_solution.pending_requests.values())
            #next_solution.check_no_requests_served_twice()
            next_obj = next_solution.compute_obj
            if next_obj > current_obj:
                current_solution = copy.deepcopy(next_solution)
                current_obj = next_obj
                print("cur obj :", current_obj)
                if current_obj == self.nb_requests: # upper bound
                    break
            else:
                for s in range(nb_swap):
                    print("swap it :", s)
                    current_solution = current_solution.swap_requests()
                    #current_solution.check_no_requests_served_twice()
        return current_solution, current_obj

    def path_relinking(self, initial_solution):
        """
        Ne pas regarder pour l'instant, encore en chantier
        """
        initial_pending_requests = initial_solution.pending_requests
        self_pending_requests = self.pending_requests
        print("initial/elite pending 1 :", initial_pending_requests.keys())
        print("self pending :", self_pending_requests.keys())
        pending_commun = [r for r in initial_pending_requests.keys() if r in self_pending_requests.keys()]
        for r in pending_commun:
            del initial_pending_requests[r]
        print("pending commun :", pending_commun)
        print("requests to insert :", initial_pending_requests.keys())
        print()

        # no need to do the path relinking if the pending requests in s1 are also pending in s2
        if len(initial_pending_requests) == 0:
            return initial_solution, initial_solution.compute_obj

        print("SELF")
        self_routes, other_requests = self.get_taxis_from_requests(initial_pending_requests.values(), viz=True)
        #other_requests = self.get_other_requests(initial_pending_requests.keys(), self_routes, viz=True)

        print()
        print("-- 1 --")
        print()
        print("INIT")
        potential_routes = initial_solution.get_potential_routes(other_requests)

        print()
        print("-- 2 --")
        print()
        improvment = False
        for req_id, req in initial_pending_requests.items():
            print("REQ ID :", req_id)
            for taxi in potential_routes[req_id]:
                print("route :", [point[1].id for point in taxi.route])
                try:
                    taxi.insert(req)
                    initial_solution.remove_request(req, pending=True)
                    improvment = True
                    print("SUCESS")
                except Exception:
                    print("FAIL")
                    continue

        print()
        print("-- 3 --")
        print()
        if not improvment:
            adjacent_requests = [r for sublist in other_requests.values() for r in sublist]
            id_adjacent_requests = [r.id for r in adjacent_requests]
            print("adjacent :", id_adjacent_requests)
            init_routes, init_other_requests = initial_solution.get_taxis_from_requests(adjacent_requests)
            #o_r = self.get_other_requests(id_adjacent_requests, other_routes, viz=True)

            print("Debut swap...")
            #simport pdb; pdb.set_trace()
            nb_succes = 0
            for sublist in init_other_requests.values():
                for r in sublist:
                    try:
                        initial_solution.swap_requests(requests=[r])
                        nb_succes += 1
                        break
                    except Exception:
                        continue
            if nb_succes == 0:
                print("no smart swap found")
            else:
                print("%d smart swap found over %d" % (nb_succes, len(init_other_requests)))

            print()
            print("-- 4 --")
            print()
            improvment = False
            potential_routes = initial_solution.get_potential_routes(other_requests)
            for req_id, req in initial_pending_requests.items():
                print("REQ ID :", req_id)
                for taxi in potential_routes[req_id]:
                    print("route :", [point[1].id for point in taxi.route])
                    try:
                        taxi.insert(req)
                        initial_solution.remove_request(req, pending=True)
                        improvment = True
                        print("SUCESS")
                    except Exception:
                        print("FAIL")
                        continue

        return initial_solution, initial_solution.compute_obj

    def get_potential_routes(self, other_requests):
        potential_routes = {}
        for req_id, other_reqs in other_requests.items():
            routes_dict, _ = self.get_taxis_from_requests(other_reqs)
            potential_routes[req_id] = list(routes_dict.values())
        return potential_routes

    def insert_requests(self, requests, nb_attempts=1):
        for k, request in enumerate(requests):
            for j in range(nb_attempts):
                taxi = random.sample(self.taxis, 1)[0]
                if request.id != taxi.route[0][1].id:
                    try:
                        #print("1")
                        taxi.insert(request)
                        #print("2")
                        self.remove_request(request, pending=True)
                        #print("3")
                        self.check_no_requests_served_twice()
                        #print("4")
                        break
                    except Exception:
                        #print("e")
                        continue
        return self

    def remove_request(self, request, pending):
        nb_taxis = len(self.taxis)
        if pending:
            self.taxis = [taxi for taxi in self.taxis if not (len(taxi.route) == 2 and taxi.route[0][1].id == request.id)]
            assert len(self.taxis) == nb_taxis - 1
        
    def swap_requests(self, nb_attempts: int=100, requests=None):
        """
        Operation used in Santos's both 2013 and 2015 paper.
        Permutation of two requests from different routes.
        """
        if requests is None:
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

                    #print("SWAP %d and %d" % (request1[0][1].id, request2[0][1].id))

                    """                    print()
                    print("1.1.1")
                    print()
                    for i, taxi in enumerate(self.taxis):
                        print("--")
                        print("number of requests served by taxi %d : %d" % (i, int(len(taxi.route)/2)))
                        seq_id = []
                        seq_time = []
                        for point in taxi.route:
                            seq_id.append(point[1].id)
                            seq_time.append(round(point[0]))
                        print(seq_id)
                        print(seq_time) """

                    self = copy.deepcopy(solution)

                    """                   print()
                    print("2.2.2")
                    print()
                    for i, taxi in enumerate(self.taxis):
                        print("--")
                        print("number of requests served by taxi %d : %d" % (i, int(len(taxi.route)/2)))
                        seq_id = []
                        seq_time = []
                        for point in taxi.route:
                            seq_id.append(point[1].id)
                            seq_time.append(round(point[0]))
                        print(seq_id)
                        print(seq_time) """

                    return self
                except Exception:
                    continue
            print("%d attempts to swap 2 requests without success" % nb_attempts)

        elif len(requests) == 2:
            try:
                solution = copy.deepcopy(self)
                taxis = solution.get_taxis_from_requests(requests)
                taxis[requests[0].id].remove(requests[0])
                taxis[requests[1].id].remove(requests[1])
                taxis[requests[0].id].insert(requests[1])
                taxis[requests[1].id].insert(requests[0])
                self = solution
                return
            except Exception:
                print("Failed to swap request %d and request %d" % (requests[0].id, requests[1].id))
                pass

        elif len(requests) == 1:
            for i in range(nb_attempts):
                try:
                    solution = copy.deepcopy(self)
                    taxi1, _ = solution.get_taxis_from_requests(requests)
                    taxi1 = taxi1[requests[0].id]
                    previous_delay = taxi1.delay
                    taxi2 = random.sample(solution.taxis, 1)[0]
                    if taxi2 == taxi1 or len(taxi2.route) == 2:
                        raise Exception("No swap between 2 same routes or with an individual route")
                    request2 = random.sample(taxi2.route, 1)[0]
                    taxi1.remove(requests[0])
                    taxi2.remove(request2[1])
                    taxi1.insert(request2[1])
                    taxi2.insert(requests[0])
                    if taxi1.delay < previous_delay:
                        self = solution
                        return
                except Exception:
                    continue
            raise Exception("%d attempts to swap 1 request with a random one without success" % nb_attempts)

        else:
            print("Wrong input :", requests)


    def get_taxis_from_requests(self, requests, viz=False) -> Dict:
        id_requests = [r.id for r in requests]
        taxis_serving_requests = {}
        other_requests = defaultdict(list)
        for taxi in self.taxis:
            route = [p[1].id for p in taxi.route]
            for req in requests:
                if any(request[1].id == req.id for request in taxi.route):
                    taxis_serving_requests[req.id] = taxi
                    seq_id = []
                    for point in taxi.route:
                        if point[1].id not in id_requests and point[1].id not in seq_id:
                            other_requests[req.id].append(point[1])
                            route.remove(point[1].id)
                        seq_id.append(point[1].id)
        assert len(taxis_serving_requests) == len(requests)

        if viz:
            visu_other_requests = {}
            for req_id, list_req in other_requests.items():
                list_req_id = [r.id for r in list_req]
                visu_other_requests[req_id] =list_req_id
            print("visu other requests :", visu_other_requests)

        return taxis_serving_requests, other_requests        
    
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

    def check_no_requests_served_twice(self):
        served_requests = [p[1].id for taxi in self.taxis for p in taxi.route]
        if not len(served_requests) / 2 == len(set(served_requests)):
            raise Exception("%d requests are served twice" % (len(served_requests) / 2 - len(set(served_requests))))
