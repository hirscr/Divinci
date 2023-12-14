
import os
import logging
import yaml
import decimal
from decimal import Decimal

class CustomFormatter(logging.Formatter):
    """ Custom Formatter does these 2 things:
    1. Overrides 'funcName' with the value of 'func_name_override', if it exists.
    2. Overrides 'filename' with the value of 'file_name_override', if it exists.
    """

    def format(self, record):
        if hasattr(record, 'func_name_override'):
            record.funcName = record.func_name_override
        if hasattr(record, 'file_name_override'):
            record.filename = record.file_name_override
        return super(CustomFormatter, self).format(record)

def Dec(val, places : int):
    quant = '1.'
    if places == None:
        quant='1.'
    elif places == 1:
        quant='0.1'
    elif places == 2:
        quant = '0.01'
    elif places == 3:
        quant = '0.001'
    elif places == 4:
        quant = '0.0001'
    elif places == 5:
        quant = '0.00001'
    elif places == 6:
        quant = '0.000001'
    elif places == 7:
        quant = '0.0000001'
    elif places >= 8:
        quant = '0.00000001'
    retval=Decimal(val).quantize(Decimal(quant), rounding=decimal.ROUND_05UP)
    return retval



def get_real_path(filename: str) -> str:
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)


def get_settings_path():
    return os.path.expanduser("~")

def get_logger(log_file_name, log_sub_dir=""):
    """ Creates a Log File and returns Logger object """

    if not log_sub_dir:
        log_dir = get_real_path("logs")
    else:
        log_dir = get_real_path(log_sub_dir)

    # Create Log file directory if not exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Build Log File Full Path
    log_path = log_file_name if os.path.exists(log_file_name) else os.path.join(log_dir, (str(log_file_name)))

    # Create logger object and set the format for logging and other attributes
    logger = logging.Logger(log_file_name)
    logger.setLevel(logging.DEBUG)

    file_logger = logging.FileHandler(log_path, 'a+')
    file_logger.setFormatter(
        CustomFormatter('%(asctime)s - %(levelname)-10s - %(filename)s - %(funcName)s - %(message)s'))
    logger.addHandler(file_logger)

    stream_logger = logging.StreamHandler()
    stream_logger.setFormatter(
        CustomFormatter('%(asctime)s - %(levelname)-10s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'))
    logger.addHandler(stream_logger)

    # https_logger = HTTPSHandler(
    #     'https://logs-01.loggly.com/inputs/5bd45371-720c-4a99-be17-1b8d3d1cefbf/tag/python')
    # formatter = logging.Formatter('{"loggerName": "%(name)s", "timestamp": "%(asctime)s", "fileName": "%(filename)s",'
    #                               '"logRecordCreationTime": "%(created)f", "functionName": "%(funcName)s","levelNo": '
    #                               '"%(levelno)s", "lineNo": "%(lineno)d", "time": "%(msecs)d","levelName": "%('
    #                               'levelname)s", "message": "%(message)s"}')
    # https_logger.setFormatter(formatter)
    # logger.addHandler(https_logger)

    # Return logger object
    return logger

def reorder(d, keys):
    for key in reversed(keys):
        d.move_to_end(key, last=False)
    return d

def round_to_hour(t : float):
    return t-(t % (60*60))

def truthy(questionable_object):
    if isinstance(questionable_object, bool):
        return questionable_object

    if isinstance(questionable_object, bytes):
        questionable_object = questionable_object.decode("UTF-8")

    if isinstance(questionable_object, str):
        questionable_object = questionable_object.lower()

        values = {
            "true": True,
            "false": False,
            "enabled": True,
            "disabled": False,
        }

        return values[questionable_object]

    raise ValueError('Could not determine truthieness of %s' % questionable_object)


def load_yaml(filename):
    try:
        f = open(os.path.join(filename), "r")
        return yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logger.info("Attempting to load %s_example as %s is missing." % (filename, filename))
        f = open(os.path.join("configuration", "%s_example" % filename), "r")
        logger.info("Loading %s succeeded." % filename)
        return yaml.load(f, Loader=yaml.FullLoader)

logger = get_logger(log_file_name="logger.log")
