from threading import Thread, Event
from time import sleep
import queue

event = Event()

def modify_variable(var, q):
    while True:
        var += 1
        q.put(var)
        sleep(.5)

def main():

    q = queue.Queue()

    my_var = 1
    t = Thread(target=modify_variable, args=(my_var,q))
    t.start()
    while True:

        print(my_var)
        my_var = q.get()
        sleep(1)


if __name__ == "__main__": 
    main()

