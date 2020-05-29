import logging

from colorama import Fore, init

init(autoreset=True)


class Logger():
    def __init__(self, log_file_path=None, **kwargs):
        handlers = [
            logging.StreamHandler()
        ]
        if log_file_path:
            handlers.append(logging.FileHandler(log_file_path))

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=handlers,
            **kwargs
        )

    @staticmethod
    def log(level, message):
        logging.log(level, message)

    @staticmethod
    def debug(message):
        Logger.log(logging.DEBUG, Fore.LIGHTYELLOW_EX + message)

    @staticmethod
    def info(message):
        Logger.log(logging.INFO, Fore.CYAN + message)

    @staticmethod
    def warning(message):
        Logger.log(logging.WARNING, Fore.YELLOW + message)

    @staticmethod
    def error(message):
        Logger.log(logging.ERROR, Fore.RED + message)
