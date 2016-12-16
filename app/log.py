#! /usr/bin/python
# -*- coding: utf-8 -*-


import logging
import logging.config
import logging.handlers
import os


DEF_LOGGING_FORMATTER = '[%(asctime)s] [%(name)s] [%(levelname)s] [%(process)d]: %(message)s'


class LoggerUtil(object):

    @staticmethod
    def format(*args, **kwargs):
        return " ".join([str(x) for x in args])


class LazyModLogger(object):

    def __init__(self, mod_name):
        self.mod_name = mod_name
        self.name = None
        self.logger = None

    def on_changed(self, root_name):
        self.name = '{}.{}'.format(root_name, self.mod_name)
        self.logger = logging.getLogger(self.name)

    def debug(self, *args, **kwargs):
        self.__get().debug(LoggerUtil.format(*args, **kwargs))

    def info(self, *args, **kwargs):
        self.__get().info(LoggerUtil.format(*args, **kwargs))

    def warn(self, *args, **kwargs):
        self.__get().warning(LoggerUtil.format(*args, **kwargs))

    def error(self, *args, **kwargs):
        self.__get().error(LoggerUtil.format(*args, **kwargs))

    def critical(self, *args, **kwargs):
        self.__get().critical(LoggerUtil.format(*args, **kwargs))

    def exception(self, *args, **kwargs):
        self.__get().exception(LoggerUtil.format(*args, **kwargs))

    def __get(self):
        if not self.logger:
            raise ValueError('Does not setup an application logger firstly.')
        return self.logger


class HqLogger(object):

    hq_logger = None

    hq_mod_loggers = {}

    @classmethod
    def get_app(cls, logger_name, filename=None):
        if logger_name is None:
            raise KeyError(
                'Cannot initialize log module.'
                'please check the logger name.')
        if cls.hq_logger is not None:
            if logger_name == cls.hq_logger.name:
                return cls.hq_logger
            cls.warn('The log will redirect from {} to {}'.format(cls.hq_logger.name, logger_name))
        cls.add(logger_name, filename)
        cls.__changed_app_logger()
        return cls.hq_logger

    @classmethod
    def get_child(cls, child_name):
        if not child_name or cls.hq_logger and child_name == cls.hq_logger.name:
            raise ValueError('Cannot get a child logger without the valid name.')
        return cls.__append_child(child_name)

    @classmethod
    def add(cls, logger_name, filename):
        if not filename:
            cls.hq_logger = logging.getLogger('hq-console')
        else:
            cls.hq_logger = logging.getLogger(logger_name)
            hq_file_handler = HqFileHandler(filename)
            hq_formatter = logging.Formatter(DEF_LOGGING_FORMATTER)
            hq_file_handler.setFormatter(hq_formatter)
            cls.hq_logger.addHandler(hq_file_handler)
            cls.hq_logger.setLevel(logging.DEBUG)
            cls.hq_logger.propagate = False
        cls.__changed_app_logger()

    @classmethod
    def __append_child(cls, mod_name):
        if mod_name not in cls.hq_mod_loggers:
            cls.hq_mod_loggers[mod_name] = LazyModLogger(mod_name)
        return cls.hq_mod_loggers[mod_name]

    @classmethod
    def __changed_app_logger(cls):
        for mod_logger in cls.hq_mod_loggers.itervalues():
            mod_logger.on_changed(cls.hq_logger.name)


class HqFileHandler(logging.FileHandler):

    def flush(self):
        super(HqFileHandler, self).flush()
        self.acquire()
        try:
            if self.stream and hasattr(self.stream, "fileno"):
                os.fsync(self.stream.fileno())
        finally:
            self.release()


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    # define all log output formatter for milio project.
    'formatters': {
        'default': {
            'format': DEF_LOGGING_FORMATTER,
        },
    },

    # define all log file handlers for milio project.
    'handlers': {
        'hq-console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    # define the special logger for each module.
    'loggers': {
        'hq-console': {
            'handlers': ['hq-console'],
            'level': 'DEBUG',
            # Do not pass the log record to the root logger or it will record twice.
            'propagate': False,
        },
    },
}


# Initialize logging from configuration.
def initialize_hq_logger():
    logging.config.dictConfig(LOGGING_CONFIG)


initialize_hq_logger()


# Define export interfaces
get_app_logger = HqLogger.get_app

get_mod_logger = HqLogger.get_child


__all__ = ['get_app_logger', 'get_mod_logger']
