import numpy as np
import pyvisa
from pyvisa import VisaIOError 
import time

class lockin():
    def __init__(self, lockin, Rbias):
        self.lockin = lockin
        self.Rbias = Rbias

    ## add all the other functions here