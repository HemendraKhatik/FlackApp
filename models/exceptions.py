class DBException(Exception):
    def __init__(self, msg=None, *args, **kwargs):
        Exception.__init__(self)
        self.message = msg
        self.args = args
        for k in kwargs.keys():
            self.__setattr__(k, kwargs.get(k))


class WordSizeException(Exception):
    def __init__(self, msg=None, min_size=3, max_size=32):
        Exception.__init__(self)
        self.message = msg if msg is not None else "The size of the word has to be between %s and %s." % (
        min_size, max_size)
        self.min_size = min_size
        self.max_size = max_size
