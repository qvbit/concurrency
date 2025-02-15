import time
import random
from threading import Thread, Semaphore, Lock

TOTAL_SPOTS = 3


class Garage:
    def __init__(self):
        self.semaphore = Semaphore(
            TOTAL_SPOTS
        )  # Ensures only TOTAL_SPOTS cars can be in the parking lot at a time
        self.cars_lock = (
            Lock()
        )  # Ensures only one thread at a time can modify parked_cars
        self.parked_cars = []

    def count_parked_cars(self):
        return len(self.parked_cars)

    def enter(self, car_name):
        self.semaphore.acquire()
        self.cars_lock.acquire()
        self.parked_cars.append(car_name)
        print(f"{car_name} parked")
        self.cars_lock.release()

    def exit(self, car_name):
        self.cars_lock.acquire()
        self.parked_cars.remove(car_name)
        print(f"{car_name} leaving")
        self.semaphore.release()
        self.cars_lock.release()


def park_car(garage: Garage, car_name: str) -> None:
    """Emulate parked car behavior"""
    garage.enter(car_name)
    time.sleep(random.uniform(1, 2))
    garage.exit(car_name)


def test_garage(garage: Garage, number_of_cars: int = 10) -> None:
    threads = []
    for car_num in range(number_of_cars):
        t = Thread(target=park_car, args=(garage, f"Car #{car_num}"))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    number_of_cars = 10
    garage = Garage()
    # test garage by concurrently arriving cars
    test_garage(garage, number_of_cars)

    print("Number of parked cars after a busy day:")
    print(f"Actual: {garage.count_parked_cars()}\nExpected: 0")
