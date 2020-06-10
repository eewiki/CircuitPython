# Riedon_BLE_plotter_rev1.py
# example for using the BLE Connect plotter
# To use, start this program, and start the Adafruit Bluefruit LE Connect app.
# Connect, and then select plotter
# Hardware:
# Adafruit nRF52840 Feather Express
# Adafruit ADS1115 ADC breakout board
# Riedon SSA-100 current sensor
#
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

fw_ver = "Riedon_BLE_plotter_rev1.py"

ble = BLERadio()
uart_server = UARTService()
advertisement = ProvideServicesAdvertisement(uart_server)

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADS object
# ads = ADS.ADS1015(i2c)
ads = ADS.ADS1115(i2c)

# Create differential channel on Pin 0 and Pin 1
chan = AnalogIn(ads, ADS.P0, ADS.P1)


#   Max ADC counts for ADS1015 = 2047
#                      ADS1115 = 32767
# The ADS1015 and ADS1115 both have the same gain options.
#
#       GAIN    RANGE (V)
#       ----    ---------
#        2/3    +/- 6.144
#          1    +/- 4.096
#          2    +/- 2.048
#          4    +/- 1.024
#          8    +/- 0.512
#         16    +/- 0.256
#

gains = (2/3, 1, 2, 4, 8, 16)
# set ADS1115 gain to 2 (max voltage= +/- 2.048)
ads.gain = 2

while True:
    print("WAITING...")
    # Advertise when not connected.
    ble.start_advertising(advertisement)
    while not ble.connected:
        pass

    # Connected
    ble.stop_advertising()
    print("CONNECTED")

    # Loop and read ADC, print and send data over bluetooth
    while ble.connected:
        print("Firmware =", fw_ver)
        #ext = 33
        #
        # set timestamp to accompany sensor data
        now = time.monotonic()
        print("time= ",now)
        # read ADS1115 adc value and voltage
        adc_cnt = chan.value
        adc_volt = chan.voltage
        print('{:5} {:5.3f}'.format(adc_cnt, adc_volt), end='')
        print()
        #uart_server.write("testing/")
        #ads.gain = 2
        print("channel value= ", adc_cnt)
        # calculate SSA-100 current
        i_SSA = (adc_cnt/32767) * 170.7
        print ("current = ", i_SSA)
        print(' ADC count= {:5} voltage = {:5.3f}\n'.format(adc_cnt, adc_volt))
        # send current reading over bluetooth UARTService
        uart_server.write('{:5.1f}\n'.format(i_SSA))
        time.sleep(0.1)

    # Disconnected
    print("DISCONNECTED")