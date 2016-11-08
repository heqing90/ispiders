# -*- coding: utf-8 -*-

from collections import OrderedDict

class HouseModel(object):
    """docstring for HouseModel"""

    HOUSE_MODEL_DEF_COLUMNS = OrderedDict({
        'xiaoqu': None,
        'type': None,
        'square': None,
        'orientation': None,
        'floor': None,
        'build': None,
        'tradedate': None,
        'persquareprice': None,
        'totalprice': None
        })

    @property
    def values(self):
        return self.__values

    def __init__(self, **kwargs):
        self.__values = {}
        # self.__values.update(self.HOUSE_MODEL_DEF_COLUMNS)
        for name, value in kwargs.iteritems():
            if name in self.HOUSE_MODEL_DEF_COLUMNS:
                self.__values[name] = value

    def __setattr__(self, name, value):
        if name in self.HOUSE_MODEL_DEF_COLUMNS:
            self.__values[name] = value
        else:
            super(HouseModel, self).__setattr__(name, value)

    def __getattr__(self, name):
        if name in self.HOUSE_MODEL_DEF_COLUMNS:
            return self.__values.get(name, 'NAV')
        else:
            return super(HouseModel, self).__getattribute__(name)
