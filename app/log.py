# -*- coding: utf-8 -*-


class ILogger(object):
    """docstring for ILogger"""

    def __init__(self, name):
        self.__name = name

    def debug(self, *args):
        print(' '.join([repr(arg) for arg in args]))

