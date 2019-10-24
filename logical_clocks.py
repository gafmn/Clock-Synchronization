from multiprocessing import Process, Pipe
from os import getpid
from datetime import datetime


def local_time(counter):
    return ' (LAMPORT_TIME={}, LOCAL_TIME={}) '.format(counter, datetime.now())


def calculate_recv_timestamp(recv_timestamp, counter):
    for i in range(len(counter)):
        counter[i] = max(counter[i], recv_timestamp[i])
    return counter


# Return updated stamp
def event(pid, counter):
    counter[pid] += 1
    print('Event in {}!'.format(pid) + local_time(counter))
    return counter


def send_message(pipe, pid, counter):
    counter[pid] += 1
    pipe.send(('Empty shell', counter))
    print('Message send from ' + str(pid) + local_time(counter))
    return counter


def recv_message(pipe, pid, counter):
    counter[pid] += 1
    message, timestamp = pipe.recv()
    counter = calculate_recv_timestamp(timestamp, counter)
    print('Message recieved at ' + str(pid) + local_time(counter))
    return counter


def process_one(pipe12):
    pid = 0
    counter = [0, 0, 0]
    counter = send_message(pipe12, pid, counter)
    counter = send_message(pipe12, pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe12, pid, counter)
    counter = event(pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe12, pid, counter)
    print('FINAL STATE COUNTER of process A')
    print(counter)


def process_two(pipe21, pipe23):
    pid = 1
    counter = [0, 0, 0]
    counter = recv_message(pipe21, pid, counter)
    counter = recv_message(pipe21, pid, counter)
    counter = send_message(pipe21, pid, counter)
    counter = recv_message(pipe23, pid, counter)
    counter = event(pid, counter)
    counter = send_message(pipe21, pid, counter)
    counter = send_message(pipe23, pid, counter)
    counter = send_message(pipe23, pid, counter)
    print('FINAL STATE COUNTER of process B')
    print(counter)


def process_three(pipe32):
    pid = 2
    counter = [0, 0, 0]
    counter = send_message(pipe32, pid, counter)
    counter = recv_message(pipe32, pid, counter)
    counter = event(pid, counter)
    counter = recv_message(pipe32, pid, counter)
    print('FINAL STATE COUNTER of process C')
    print(counter)


if __name__ == '__main__':
    one_two, two_one = Pipe()
    two_three, three_two = Pipe()
    process1 = Process(target=process_one, args=(one_two,))
    process2 = Process(target=process_two, args=(two_one, two_three))
    process3 = Process(target=process_three, args=(three_two,))

    process1.start()
    process2.start()
    process3.start()

    process1.join()
    process2.join()
    process3.join()
