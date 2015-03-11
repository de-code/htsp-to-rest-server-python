class StreamToLoggingRedirect(object):
    def __init__(self, logger, level, fallback):
        self.logger = logger
        self.level = level
        self.invokation = 0

    def write(self, thing):
        self.invokation = self.invokation + 1
        try:
            if (self.invokation == 1):
                self.logger.log(self.level, thing)
            else:
                # avoid recursive calls
                fallback.write(thing)
        finally:
            self.invokation = self.invokation - 1
