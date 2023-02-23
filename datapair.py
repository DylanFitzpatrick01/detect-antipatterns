# Class that stores variables passed in from Clang

class DataPair():
    variable = ""
    t = ""
    line_number = 0

    def __init__(self, variable, t):
        self.variable = variable
        self.t = t

