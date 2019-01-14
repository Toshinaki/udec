#!/usr/bin/python

###############################################################################
## Description
###############################################################################

###############################################################################
## Imports 
###############################################################################
import logging
from functools import wraps, partial
from pathlib import Path
from inspect import isclass

###############################################################################
## CONSTANTS & HELPER FUNCTIONS
###############################################################################
LEVELS = {
    'critical': logging.CRITICAL,
    'error':    logging.ERROR,
    'warning':  logging.WARNING,
    'info':     logging.INFO,
    'debug':    logging.DEBUG
}

def create_logger(name='UsefulLogger', level='info', filepath='ulog.log', extra_handlers=[]):
    '''
    Creates a logging object and returns it
    '''
    logger = logging.getLogger(name)
    if logger.hasHandlers(): logger.handlers.clear()
    logger.setLevel(LEVELS.get(level, 'info'))

    filepath = Path(filepath)
    if not filepath.exists(): filepath.touch()
    file_handler = logging.FileHandler(filepath)
    fmt = '\n' + '='*80 + '\n%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    for hdl in extra_handlers:
        logger.addHandler(hdl)
    return logger

###############################################################################
## CLASSES
###############################################################################
class Ulogger(object):

    '''
    A decorator for variant use
    '''

    def __init__(self, ltype='excexe', logger=None, *args, **kwargs):
        self.ltype = ltype
        self.logger = logger
        self.args = args
        self.kwargs = kwargs

        self.mode = 'decorating'
    
    def __call__(self, *args, **kwargs):
        if self.mode == 'decorating':
            if self.ltype == 'execution':
                self.func = self.exe_logger(args[0], *self.args, **self.kwargs)
            elif self.ltype == 'exception':
                self.func = self.exception_logger(args[0], *self.args, **self.kwargs)
            elif self.ltype == 'excexe':
                self.func = self.excexe_logger(args[0], *self.args, **self.kwargs)
            self.mode = 'calling'
            return self
        
        if len(args) > 0:
            if hasattr(args[0], 'logger'):
                self.logger = args[0].logger
        elif self.logger is None:
            self.logger = create_logger()
        r = self.func(*args, **kwargs)
        return r

    def __get__(self, instance, cls):
        return partial(self.__call__, instance)

    def exe_logger(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            self.logger.info('{}() - Starting execution...'.format(func.__name__))
            r = func(*args, **kwargs)
            self.logger.info('{}() - Execution ended'.format(func.__name__))
            return r
        return decorator
    
    def exception_logger(self, func, re_raise=True):
        @wraps(func)
        def decorator(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.logger.exception('{}() - A {} occurred.'.format(func.__name__, e.__class__.__name__))
                if re_raise:
                    raise
                else:
                    return False
        return decorator
    
    def excexe_logger(self, func, re_raise=True):
        @wraps(func)
        def decorator(*args, **kwargs):
            self.logger.info('{}() - Starting execution...'.format(func.__name__))
            try:
                r = func(*args, **kwargs)
            except Exception as e:
                self.logger.exception('{}() - A {} occurred.'.format(func.__name__, e.__class__.__name__))
                if re_raise:
                    raise
                else:
                    return False
            else:
                self.logger.info('{}() - Execution ended'.format(func.__name__))
                return r
        return decorator


# def exception_logger(func=None, logger=None, reraise=True):
#     '''
#     A decorator that wraps the passed in function and logs 
#     exceptions should one occur
#     '''
#     if func is None:
#         return partial(exception_logger, logger=logger, reraise=reraise)
    
#     if logger is None:
#         logger = create_logger()

#     @wraps(func)
#     def decorator(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except Exception as e:
#             logger.exception('{} - A {} occurred.'.format(func.__name__, e.__class__.__name__))
#             if reraise:
#                 raise
#             else:
#                 return False
#     return decorator