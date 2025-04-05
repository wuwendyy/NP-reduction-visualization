from abc import abstractmethod

class Element:
    # display to pygame
    @abstractmethod
    def display(self, screen):
        raise NotImplementedError

    # parse in from file
    @abstractmethod
    def parse(self, filename):
        raise NotImplementedError
