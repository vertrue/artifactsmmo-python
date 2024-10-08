import threading
import time
from characters import attacker, weaponcrafter, gearcrafter, jewelrycrafter, cooker


def run_attacker():
    attacker.pre_run()
    while True:
        attacker.run()
        time.sleep(0.1)


def run_weaponcrafter():
    weaponcrafter.pre_run()
    while True:
        weaponcrafter.run()
        time.sleep(0.1)


def run_gearcrafter():
    gearcrafter.pre_run()
    while True:
        gearcrafter.run()
        time.sleep(0.1)


def run_jewelrycrafter():
    jewelrycrafter.pre_run()
    while True:
        jewelrycrafter.run()
        time.sleep(0.1)


def run_cooker():
    cooker.pre_run()
    while True:
        cooker.run()
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
