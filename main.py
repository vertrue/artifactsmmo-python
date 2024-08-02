import threading
import time
from characters import attacker, weaponcrafter, gearcrafter, jewelrycrafter, coocker


def run_attacker():
    while True:
        attacker.run()
        time.sleep(0.1)


def run_weaponcrafter():
    while True:
        weaponcrafter.run()
        time.sleep(0.1)


def run_gearcrafter():
    while True:
        gearcrafter.run()
        time.sleep(0.1)


def run_jewelrycrafter():
    while True:
        jewelrycrafter.run()
        time.sleep(0.1)


def run_cooker():
    while True:
        coocker.run()
        time.sleep(0.1)


if __name__ == "__main__":
    attacker_thread = threading.Thread(target=run_attacker)
    weaponcrafter_thread = threading.Thread(target=run_weaponcrafter)
    gearcrafter_thread = threading.Thread(target=run_gearcrafter)
    jewelrycrafter_thread = threading.Thread(target=run_jewelrycrafter)
    cooker_thread = threading.Thread(target=run_cooker)

    attacker_thread.start()
    weaponcrafter_thread.start()
    gearcrafter_thread.start()
    jewelrycrafter_thread.start()
    cooker_thread.start()

    attacker_thread.join()
    weaponcrafter_thread.join()
    gearcrafter_thread.join()
    jewelrycrafter_thread.join()
    cooker_thread.join()
