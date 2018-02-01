class GenericImageSource(object):
    def __init__(self):
        self.__stopped = False

    @property
    def stopped(self):
        return self.__stopped

    @stopped.setter
    def stopped(self, val):
        self.__stopped = val

    def start(self):
        raise Exception("Should be implemented by subclass")

    def stop(self):
        raise Exception("Should be implemented by subclass")

    def get_image(self):
        raise Exception("Should be implemented by subclass")
