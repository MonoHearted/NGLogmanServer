from __future__ import division
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from functools import wraps

logger = logging.getLogger(__name__)

Units = ['BYTES', 'KB', 'MB', 'GB', 'TB']
MUL = [1, 1 << 10, 1 << 20, 1 << 30, 1 << 40]

def acronymTitleCase(string):
    string = string.title()
    acronyms = ['KB', 'MB', 'GB', 'TB', 'CPU']
    for acronym in map(str.title, acronyms):
        if acronym in string:
            string = string.replace(acronym, acronym.upper())
    return string

def timestamp(dt):
    """
    Convert a datetime object to the timestamp format used for file names.
    :param dt: The datetime object
    :return: The formatted datetime string
    """
    return dt.isoformat().replace(':', '-').replace('.', '_').partition('+')[0]

def to_aware(dt):
    """
    Converts a timezone-naive datetime to a datetime-aware object.
    :param dt: A datetime object.
    :return: A timezone-aware datetime object.
    """
    from datetime import datetime
    from django.utils import timezone
    if not isinstance(dt, datetime):
        from dateutil import parser
        dt = parser.parse(dt, ignoretz=True)

    if timezone.is_naive(dt):
        dt = dt.replace(tzinfo=timezone.utc)

    return dt

def convertBytesTo(unit):
    """
    A decorator that modifies all byte units to the desired unit.
    :param unit: The desired unit (KB, MB, GB etc.)
    """
    if (not unit in Units):
        raise ValueError("Invalid unit <%s>" % unit)
    index = Units.index(unit)
    multiple = MUL[index]

    def setUnitDecorator(f):
        @wraps(f)
        def funcWrapper(*args, **kwargs):
            logger.debug("Ready to set unit to <%s>" % unit)
            result =f(*args, **kwargs)
            retDict = dict()
            if (not isinstance(result, dict)):
                raise ValueError("Invalid type for returned result")
            for key, value in result.items():
                if (not isinstance(key, str)):
                    raise ValueError("Invalid type for key name, str expected")
                if ('BYTES' in key.upper()):
                    try:
                        if(isinstance(value, list)):
                            value[:]=[int(x) / multiple for x in value]
                        else:
                            value = int(value) / multiple
                    except:
                        raise ValueError("Invalid type for value, "
                                         "str formatted integer is expected")
                    key = key.upper().replace('BYTES', unit)
                    retDict[key] = value
                else:
                    retDict[key] = value
            return retDict

        return funcWrapper

    return setUnitDecorator


class Singleton(type):
    """
    An implementation of a Singleton class.
    """
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


class singletonThreadPool(ThreadPoolExecutor,metaclass=Singleton):
    """
    A singleton ThreadpoolExecutor class.
    """
    pass
