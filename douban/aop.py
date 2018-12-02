import time


def consume_time(func):
    def temp_fun(*args, **args2):
        t0 = int(time.time() * 1000)
        back = func(*args, **args2)
        t1 = int(time.time() * 1000)
        print("{} consume time:{} ms".format(func, (t1 - t0)))
        return back

    return temp_fun
