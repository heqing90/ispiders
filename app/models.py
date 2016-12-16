# -*- coding: utf-8 -*-

from collections import OrderedDict
from log import get_mod_logger


class HouseModel(object):
    """docstring for HouseModel"""

    HOUSE_MODEL_DEF_COLUMNS = OrderedDict({
        'xiaoqu': '小区',
        'type': '户型',
        'square': '面积',
        'orientation': '朝向',
        'floor': '楼层',
        'build': '竣工',
        'tradedate': '交易日期',
        'persquareprice': '单价',
        'totalprice': '总价'})

    logger = get_mod_logger('House')

    @property
    def values(self):
        return self.__values

    def __init__(self, **kwargs):
        self.__values = {}
        # self.__values.update(self.HOUSE_MODEL_DEF_COLUMNS)
        for name, value in kwargs.iteritems():
            if name in self.HOUSE_MODEL_DEF_COLUMNS:
                self.__values[name] = value
        self.logger.info('Get house info: {}'.format(self.values))

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
