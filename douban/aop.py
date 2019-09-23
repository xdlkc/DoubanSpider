import time


def consume_time(func):
    """
    计算函数耗时切面（毫秒）
    :param func:
    :return:
    """

    def temp_fun(*args, **args2):
        t0 = int(time.time() * 1000)
        back = func(*args, **args2)
        t1 = int(time.time() * 1000)
        print("{} consume time:{} ms".format(func, (t1 - t0)))
        return back

    return temp_fun