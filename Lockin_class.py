import time
import numpy as np
from tqdm import tqdm


class lockin:
    def __init__(self, lockin, temp_reader, Rbias):
        self.lockin = lockin
        self.temp_reader = temp_reader
        self.Rbias = Rbias

    def set_output(self, n=1):
        self.lockin.write(f"ISRC {n}")

    def set_voltage(self, voltage):  # ex set_voltage(0.100) sets to 100 mV
        self.lockin.write(f"SLVL {voltage}")

    def read_voltage(self):  # reads frequency
        return float(self.lockin.query("SLVL?"))

    def set_frequency(self, freq):
        self.lockin.write(f"FREQ {freq}")

    def read_frequency(self):
        return float(self.lockin.query("FREQ?"))

    def read_x(self):  # reads x
        return float(self.lockin.query("OUTP? 0"))

    def read_y(self):  # reads y
        return float(self.lockin.query("OUTP? 1"))

    def read_r(self):
        return float(self.lockin.query("OUTP? 2"))

    def read_theta(self):
        return float(self.lockin.query("OUTP? 3"))

    def calculate_current(self):
        V = self.read_voltage()
        return V / self.Rbias

    def calculate_sample_resistance(self):
        voltage = self.read_r()
        current = self.calculate_current()
        return voltage / current  # == R = I/V

    def read_temperature(self, is_lakeshore=True):
        if is_lakeshore:
            return float(self.temp_reader.query("KRDG? 0"))
        else:
            return float(self.temp_reader.query("2B?"))

    def initialize(self, v, f, n=1):
        self.set_voltage(voltage=v)
        self.set_frequency(freq=f)
        self.set_output(n=n)
        self.lockin.write("IRNG 0.1V")
        self.lockin.write("SCAL 9")

    def log_data(self, filename, is_lakeshore=True, sampling_spacing=1, init_sleep=30, **kwargs):
        """
        Parameters
        ----------
        filename : float
            Text file path to save calibration.
        sampling_spacing : float, optional
            Obtains data after x seconds of waiting.
        init_sleep : float, optional
            Time (seconds) to sleep before collecting data. For lock-in
            to stabilize after **`initilize`**.
        kwargs : dict\n
            acceptable parameters:\n
                - seconds
                - minutes
                - hours
                - days
        """
        if is_lakeshore:
            while self.read_temperature(is_lakeshore) != 0: 
                time.sleep(60)

        time.sleep(init_sleep)

        if "seconds" in kwargs:
            N = kwargs["seconds"] / sampling_spacing
        elif "minutes" in kwargs:
            N = 60 * kwargs["minutes"] / sampling_spacing
        elif "hours" in kwargs:
            N = 3600 * kwargs["hours"] / sampling_spacing
        elif "days" in kwargs:
            N = 24 * 3600 * kwargs["days"] / sampling_spacing
        else:
            print("what?")

        N = int(np.ceil(N))

        header = ["Phase", "Resistance (Ohms)", "Temperature (K)"]
        with open(filename, "a") as file:
            file.write("\t".join(header))
            file.write("\n")

            p_bar = tqdm(range(N), desc="Progress", ncols=200, unit="Points")
            for __ in p_bar:
                phase = self.read_theta()
                resistance = self.calculate_sample_resistance()
                temperature = self.read_temperature(is_lakeshore=is_lakeshore)

                np.savetxt(
                    file, np.array([phase, resistance, temperature]).reshape(1, -1), delimiter="\t"
                )

                p_bar.set_postfix_str(f"Temperature: {temperature:.4g} K")
                time.sleep(sampling_spacing)
