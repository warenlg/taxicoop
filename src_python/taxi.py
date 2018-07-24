import copy
from typing import Callable, List

from utils import time


class Taxi:

    def __init__(self, request, capacity: int=2, speed: int=40):
        """
        list of request indices in the same order as the taxi drives them.
        positive indices stand for PU points when negative indices stand for DO points.
        """
        B_source = request.PU_datetime()[0]
        B_destination = request.PU_datetime()[0] + time(request.PU_coordinates(), request.DO_coordinates())
        # e.g. [(B3_source, request_3, PU_coordinates_3), (B6_source, request_6, PU_coordinates_6),
        #       (B3_destination, request_3, DO_coordinates_3), (B6_destination, request_6, DO_coordinates_6)]
        self.route = [[B_source, request, request.PU_coordinates()], [B_destination, request, request.DO_coordinates()]]
        self.capacity = capacity
        self.speed = speed

    def insert(self, request: Callable):
        """
        TODO
        """
        for pu in range(len(self.route) + 1):
            route1 = copy.deepcopy(self.route)
            route1.insert(pu, [request.PU_datetime()[0], request, request.PU_coordinates()])
            for do in range(pu + 1, len(route1) + 1):
                try:
                    route2 = copy.deepcopy(route1)
                    route2.insert(do, [request.PU_datetime()[0] + time(request.PU_coordinates(), request.DO_coordinates()),
                                    request, request.DO_coordinates()])
                    self.is_valid(route2)
                    self.update_delivery_datetimes(route2)
                    self.is_valid(route2)
                    self.route = route2
                    return
                except Exception:
                    continue
        raise Exception("could not insert request %d into the route %s" % (request.id, self.route))

    def remove(self, request: Callable):
        """
        TODO
        """
        self.route = [req for req in self.route if req[1] != request]

    def get_loading_timeline(self, route) -> List[int]:
        served_request = []
        loading_timeline = [0]
        for x in route:
            if x[1].id not in served_request:
                loading_timeline.append(loading_timeline[-1] + 1)
                served_request.append(x[1].id)
            else:
                loading_timeline.append(loading_timeline[-1] - 1)

        # for future tests
        assert len(loading_timeline) == len(route) + 1
        assert loading_timeline[-1] == 0

        return loading_timeline

    def is_valid(self, route) -> bool:
        """
        check:
        1. the capacity constraint
        2. the time windows of the passengers
        """

        # check the capacity constraint
        loading_timeline = self.get_loading_timeline(route)
        if max(loading_timeline) > self.capacity:
            raise Exception("The maximum number of passengers served at the same time %d"
                            "exceed the taxi capacity %d" % (max(loading_timeline, self.capacity)))

        # check the time windows of the passengers
        served_requests = []
        for i in range(len(route)):

            # source point
            if route[i][1].id not in served_requests and route[i][0] > route[i][1].PU_datetime()[1]:
                raise Exception("The taxi can not pick up the client %d after the end of the time window %d"
                                % (route[i][1].id, route[i][1].PU_datetime()[1]))
            
            # destination point
            elif route[i][1].id in served_requests and route[i][0] > route[i][1].DO_datetime()[1]:
                raise Exception("The taxi can not drop off the client %d after the end of the time window %d"
                                % (route[i][1].id, route[i][1].DO_datetime()[1]))
            served_requests.append(route[i][1].id)

    def update_delivery_datetimes(self, route):
        for i in range(len(route)-1):
            time_to_next_point = time(route[i][2], route[i+1][2])
            if route[i][0] + time_to_next_point > route[i+1][0]:
                route[i+1][0] = route[i][0] + time_to_next_point
            
            # source point
            #if self.route[i][1] not in served_requests:
            #    if self.route[i][0] < self.route[i][1].PU_datetime()[0]:
            #        self.route[i][0] = self.route[i][1].PU_datetime()[0]
            # destination point
            #else:
            #    if self.route[i][0] < self.route[i][1].DO_datetime()[0]:
            #        self.route[i][0] = self.route[i][1].DO_datetime()[0]
