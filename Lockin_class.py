import numpy as np
import pyvisa
from pyvisa import VisaIOError 
import time

class lockin():
    def __init__(self, lockin, Rbias):
        self.lockin = lockin
        self.Rbias = Rbias 
        
    def set_voltage(self, voltage): # ex set_voltage(0.100) sets to 100 mV
        self.lockin.write(f"SLVL {voltage}")

    def read_voltage(self): # reads frequency
        return float(self.lockin.query("SLVL?"))
    
    def set_frequency(self, freq):
        self.lockin.write(f"FREQ {freq}")

    def read_frequency(self):
        return float(self.lockin.query("FREQ?"))
    
    def read_x(self):# reads x
        return float(self.lockin.query("OUTP? 0"))
    
    def read_y(self): #reads y
        return float(self.lockin.query("OUTP? 1"))
    
    def read_r(self):
        return float(self.lockin.query("OUTP? 2"))
    
    def read_theta(self):
        return float(self.lockin.query("OUTP? 3"))
    
    def read_ab(self):
        return float(self.lockin.query(""))
    
    def calculate_current(self):
        V = self.read_voltage()
        return V / self.Rbias
    
    def calculate_sample_resistance(self):
        voltage = self.read_r()
        current = self.calculate_current()
        return voltage / current # == R = I/V
    
    def log_data(self, filename):
        with open(filename, 'a') as file:
            file.write(
                "Theta  SampleR"
            )
            i= 0
            while i<5:
                theta = self.read_theta()
                sampleR = self.calculate_sample_resistance()

                file.write (
                    f"{theta}   "
                    f"{sampleR}\n"
                )
                time.sleep(1)
                i+=1



    ## add all the other functions here