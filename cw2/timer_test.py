import threading
import time

def timer():
    start = round(time.time() * 1000)
    while True:
        yield round(time.time() * 1000) - start


if __name__ == '__main__':
    t = timer() #start the timer
    TIMEOUT = 5000
    while True:
        time_passed = next(t)
        print(time_passed)
        if (time_passed >= TIMEOUT):#if we have reached the timeout
            t = timer() # restart timer
            continue # go back to beginning of loop and try again
