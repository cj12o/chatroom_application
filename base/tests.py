# from django.test import TestCase

# Create your tests here.

from queue import Queue

q=Queue()

for x in range(0,10):
    q.put(x)
    print(f"QUEUE ELE inserted :{x}")

def main():
    global q

    for x in range(0,q.qsize()):
        print(f"QUEUE ELE :{q.get()}")


if __name__=="__main__":
    main()