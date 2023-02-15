from datetime import datetime
import functools
from typing import Callable

history_list = []

class CommandLog:
    def __init__(self, command, input_time, hotels):
        self.command = command
        self.input_time = input_time
        self.hotels = hotels


def logging_decorator(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapped_func(params, history=None):
        if history is None:
            history = history_list

        print('история:', history)
        input_time = datetime.now()
        print(params)
        result = func(params)

        if isinstance(result, type):
            hotels = None
        else:
            hotels = result

        if len(history) == 5:
            history.pop(0)

        history.append(CommandLog(
            command=func.__name__,
            input_time=input_time,
            hotels=hotels))

        return result

    return wrapped_func