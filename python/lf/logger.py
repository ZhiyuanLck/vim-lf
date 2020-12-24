import logging
from .option import lfopt

class Logger(object):
    def __init__(self):
        self.normal = logging.getLogger("NORMAL")
        self.move = logging.getLogger("MOVE")
        self.change = logging.getLogger("CHANGE")
        self.open = logging.getLogger("OPEN")
        for name in ["normal", "move", "change", "open"]:
            logger = getattr(self, name)
            logger.setLevel(logging.DEBUG)
            handler = logging.FileHandler(lfopt.log_path)
            formatter = logging.Formatter(
                    '[%(asctime)s] [%(name)-6s] [%(levelname)-7s] --- %(message)s (%(filename)s:%(lineno)s)',
                    '%Y-%m-%d %H:%M:%S'
                    )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

logger = Logger()
