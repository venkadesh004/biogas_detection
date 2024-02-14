from machine import Pin, ADC
from micropython import const
import utime
from math import exp, log

class MQ2(object):

    # Defining the Calibration Constants
    MQ_SAMPLE_TIMES_CALIBRATION = const(5)
    MQ_SAMPLE_INTERVAL_CALIBRATION = const(500)

    def _init_(self, pinData, boardResistance = 10, baseVoltage = 3.3, sample_counts = 1):

        """
            This is the Constructor function.
            pinData -> It is the ADC pin which is connected with the sensor
            boardResistance -> This is the default BoardResistance
			baseVoltage -> This the voltage provided to the sensor from the board
			time_interval -> Time interval for taking records for calculating each value
            sample_counts -> The average number of samples to be taken on counting each values
        """

        self._baseVoltage = baseVoltage
        self.pinData = ADC(pinData)
        self._boardResistance = boardResistance
        self._stateCalibrate = False
        self._sampleCounts = sample_counts

    def calibrate(self):
		
        """
            This is the calibration function.
            It sets the basic calibration value for the system.
            Must be called every time in the start of the program
		"""

        ro = 0
        print("Calibrating...")
        for i in range(MQ_SAMPLE_TIMES_CALIBRATION):
            print("Getting Data for Calibration Stage: {0}. Calibration Completes in {1} seconds".format(i+1, (MQ_SAMPLE_INTERVAL_CALIBRATION (MQ_SAMPLE_TIMES_CALIBRATION-i+1))/1000))
            ro += self.calculateResistance(self.pinData.read_u16())
            utime.sleep_ms(MQ_SAMPLE_INTERVAL_CALIBRATION)

        ro = ro/(MQ_SAMPLE_TIMES_CALIBRATION)
        print("Calibration Completed..")

        self._ro = ro
        self._stateCalibrate = True
        pass

    def calculateResistance(self, rawADC):

        """
            Used to calculate the resistance of the current input
		"""

        vrl = rawADC*(self._baseVoltage / 65535)
        rsAir = (self._baseVoltage - vrl)/vrl*self._boardResistance

        return rsAir

    def readRS(self):

        """
            Used to calculate the value of each sample
		"""

        rs = 0
        for i in range(self._sampleCounts):
            rs += self.calculateResistance(self.pinData.read_u16())
        rs = rs/(self._sampleCounts)
    
        return rs

    def getReading(self):
		
        """
            Must be called for each samples
		"""

        val = self.readRS()
        return [val/self._ro, val-self._ro, val]


# Pin Number of the ADC: 26
# Time interval between each interval: 0.1 s
# No of samples for Each Counts: 1

pin = 26
time_interval = 0.1
sensor = MQ2(pinData = pin, baseVoltage=3.3, sample_counts=1)

sensor.calibrate()
led = Pin(3, Pin.OUT)

print("Base Resistance: {0}".format(sensor._ro))

while True:
    reading = sensor.getReading()
    print("Gas Detected. Current Resistance: {0}, Difference: {1}, Ratio: {2}".format(reading[2], reading[1], reading[0]))
    if (reading[1] < -3):
        led.on()
    else:
        led.off()
    # Time interval between each samples
    utime.sleep(time_interval)