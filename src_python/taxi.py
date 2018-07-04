from typing import Tuple, List

from haversine import haversine


class Taxi:

    def __init__(self, capacity: int=2, speed: int=40):
        """
        list of request indices in the same order as the taxi drives them.
        positive indices stand for PU points when negative indices stand for DO points.
        """
        self.route = []  # e.g. [3, 6, -3, -6]
        self.served_request = []  # e.g. [request_3, request_6]
        self.capacity = capacity
        self.speed = speed

    def add_request(self, request, PU_position: int, DO_position: int):
        """
        TODO
        """
        self.route[PU_position] = request.id
        self.route[DO_position] = - request.id
        self.served_requests.append(request)

    def remove_request(self, request):
        """
        TODO
        """
        self.route.remove(request.id)
        self.route.remove(- request.id)
        self.served_requests.remove(request)

    def get_loading_timeline(self):
        loading_timeline = [0]
        for request_id in self.route:
            if request_id > 0:
                loading_timeline.append(loading_timeline[-1] + 1)
            else:
                loading_timeline.append(loading_timeline[-1] - 1)

        # for future tests
        assert len(loading_timeline) == len(self.route) + 1
        assert loading_timeline[-1] == 0

        return loading_timeline

    def is_valid(self, distance=haversine) -> bool:
        """
        check:
        1. the capacity constraint
        2. the time windows of the passengers
        """

        # check the capacity constraint
        loading_timeline = self.get_loading_timeline()
        if max(loading_timeline) > self.capacity:
            return False

        # check the time windows of the passengers
        t = self.served_requests[self.route[0]].PU_datetime()[1]
        current_point = self.served_requests[self.route[0]].PU_coordinates()
        for next_request_id in self.route[1:]:
            if next_request_id > 0:
                next_request = self.served_requests[next_request_id]
                next_point = next_request.PU_coordinates()
            else:
                next_request = self.served_requests[-next_request_id]
                next_point = next_request.DO_coordinates()
            # compute the arrival time to the next point
            t += distance(current_point, next_point) / self.speed
            if next_request_id > 0 and t > next_request.PU_datetime()[0]:
                return False
            elif next_request_id < 0 and t > next_request.DO_datetime()[1]:
                return False
            else:
                current_point = next_point
        return True
