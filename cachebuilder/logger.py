import logging
import io

# Set log level here
loglevel = logging.INFO

class Logger(object):
    """
    Detain all the logs
    """
    _instance = None
    stream = io.StringIO()

    def __new__(cls, *args, **kwargs):
        """
        We all love singletons
        """
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        logging.basicConfig(stream=self.stream,level=loglevel)

    def getAll(self):
        self.stream.seek(0)
        str = self.stream.read()
        self.stream = io.StringIO()
        logging.basicConfig(stream=self.stream,level=loglevel)
        return str
