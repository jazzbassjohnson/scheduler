import unittest


from traveling_zip import (Order, Hospital, ZipScheduler)
import numpy as np

# Each Nest has this many Zips
NUM_ZIPS = 10

# Each Zip can carry between 1 and this many packages per flight
# Note: a Zip can deliver more than 1 package per stop
MAX_PACKAGES_PER_ZIP = 3

# Zips fly a constant groundspeed (m/s)
ZIP_SPEED_MPS = 30

# Zips can fly a total roundtrip distance (m)
ZIP_MAX_CUMULATIVE_RANGE_M = 160 * 1000  # 160 km -> meters

# The two acceptable priorities
EMERGENCY = "EMERGENCY"
RESUPPLY = "Resupply"



class TestZipScheduler(unittest.TestCase):
    def setUp(self):
        self.hospital_a = Hospital("Hospital A", 1000, 1000)
        self.hospital_b = Hospital("Hospital B", 2000, 2000)
        self.hospital_c = Hospital("Hospital C", 3000, 3000)
        self.hospitals = {
            "Hospital A": self.hospital_a,
            "Hospital B": self.hospital_b,
            "Hospital C": self.hospital_c,
        }
        self.scheduler = ZipScheduler(
            hospitals=self.hospitals,
            num_zips=NUM_ZIPS,
            max_packages_per_zip=MAX_PACKAGES_PER_ZIP,
            zip_speed_mps=ZIP_SPEED_MPS,
            zip_max_cumulative_range_m=ZIP_MAX_CUMULATIVE_RANGE_M,
        )

    def test_calculate_distance(self):
        self.assertEqual(self.scheduler.calculate_distance((0, 0), (1000, 1000)), 2000)
        self.assertEqual(self.scheduler.calculate_distance((1000, 1000), (2000, 2000)), 2000)
        self.assertEqual(self.scheduler.calculate_distance((0, 0), (3000, 3000)), 6000)

    def test_queue_order(self):
        order1 = Order(0, self.hospital_a, EMERGENCY)
        order2 = Order(0, self.hospital_b, Resupply)
        self.scheduler.queue_order(order1)
        self.scheduler.queue_order(order2)
        self.assertEqual(len(self.scheduler.unfulfilled_orders), 2)
        self.assertEqual(self.scheduler.unfulfilled_orders[0], order1)
        self.assertEqual(self.scheduler.unfulfilled_orders[1], order2)

    def test_launch_flights(self):
        order1 = Order(0, self.hospital_a, EMERGENCY)
        order2 = Order(0, self.hospital_b, Resupply)
        order3 = Order(0, self.hospital_c, Resupply)
        self.scheduler.queue_order(order1)
        self.scheduler.queue_order(order2)
        self.scheduler.queue_order(order3)
        flights = self.scheduler.launch_flights(current_time=0)
        self.assertEqual(len(flights), 1)
        self.assertEqual(len(flights[0].orders), 3)
        self.assertEqual(flights[0].orders[0], order1)
        self.assertEqual(flights[0].orders[1], order2)
        self.assertEqual(flights[0].orders[2], order3)
        self.assertEqual(len(self.scheduler.unfulfilled_orders), 0)

    def test_flight_limits(self):
        order1 = Order(0, self.hospital_a, EMERGENCY)
        order2 = Order(0, self.hospital_b, EMERGENCY)
        order3 = Order(0, self.hospital_c, EMERGENCY)
        order4 = Order(0, self.hospital_a, Resupply)
        order5 = Order(0, self.hospital_b, Resupply)
        self.scheduler.queue_order(order1)
        self.scheduler.queue_order(order2)
        self.scheduler.queue_order(order3)
        self.scheduler.queue_order(order4)
        self.scheduler.queue_order(order5)
        flights = self.scheduler.launch_flights(current_time=0)
        self.assertEqual(len(flights), 2)  # Since max packages per zip is 3
        self.assertEqual(len(flights[0].orders), 3)
        self.assertEqual(len(flights[1].orders), 2)


class TestMeanDeliveryTime(unittest.TestCase):
    def setUp(self):
        self.hospital_a = Hospital("Hospital A", 1000, 1000)
        self.hospital_b = Hospital("Hospital B", 2000, 2000)
        self.hospital_c = Hospital("Hospital C", 3000, 3000)
        self.hospitals = {
            "Hospital A": self.hospital_a,
            "Hospital B": self.hospital_b,
            "Hospital C": self.hospital_c,
        }
        self.scheduler = ZipScheduler(
            hospitals=self.hospitals,
            num_zips=NUM_ZIPS,
            max_packages_per_zip=MAX_PACKAGES_PER_ZIP,
            zip_speed_mps=ZIP_SPEED_MPS,
            zip_max_cumulative_range_m=ZIP_MAX_CUMULATIVE_RANGE_M,
        )

    def calculate_delivery_times(self, orders):
        # Reset the scheduler for each test case
        self.scheduler._unfulfilled_orders = []
        for order in orders:
            self.scheduler.queue_order(order)

        current_time = 0
        delivery_times = []
        while self.scheduler.unfulfilled_orders:
            flights = self.scheduler.launch_flights(current_time)
            for flight in flights:
                flight_time = 0
                for order in flight.orders:
                    hospital_position = (order.hospital.north_m, order.hospital.east_m)
                    flight_time += self.scheduler.calculate_distance((0, 0), hospital_position) / ZIP_SPEED_MPS
                delivery_times.extend([current_time + flight_time] * len(flight.orders))
            current_time += 60  # Simulate the next minute
        return delivery_times

    def test_mean_delivery_time(self):
        order_times = [0, 60, 120, 180, 240]
        orders_list = [
            [Order(time, self.hospital_a, EMERGENCY) for time in order_times],
            [Order(time, self.hospital_b, Resupply) for time in order_times],
            [Order(time, self.hospital_c, EMERGENCY) for time in order_times],
            [Order(time, self.hospital_a, Resupply) for time in order_times],
            [Order(time, self.hospital_b, EMERGENCY) for time in order_times],
            [Order(time, self.hospital_c, Resupply) for time in order_times],
        ]

        for i, orders in enumerate(orders_list):
            delivery_times = self.calculate_delivery_times(orders)
            mean_delivery_time = np.mean(delivery_times)
            print(f"Mean Delivery Time for Test Case {i + 1} with {len(orders)} orders: {mean_delivery_time:.2f} seconds")

if __name__ == "__main__":
    unittest.main()
