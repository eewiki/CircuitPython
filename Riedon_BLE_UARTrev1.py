# Riedon_BLE_UARTrev1.py
# Basic example for using the BLE Connect UART
# To use, start this program, and start the Adafruit Bluefruit LE Connect app.
# Connect, and then select UART
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

fw_ver = "Riedon_BLE_UARTrev1.py"

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

# Create a sinlge ended channel on Pin 0
#   Max counts for ADS1015 = 2047
#                  ADS1115 = 32767
#chan = AnalogIn(ads, ADS.P0)
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
# set gain to 2
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

    # Loop and read packets
    while ble.connected:
        print("Firmware =", fw_ver)
        text = 33
        print("text =", text)
        #ads.gain = gains[0]
        # generate timestamp
        now = time.monotonic()
        print("time= ",now)
        # read ADS1115 adc value and voltage
        adc_cnt = chan.value
        adc_volt = chan.voltage
        print('{:5} {:5.3f}'.format(adc_cnt, adc_volt), end='')
        #for gain in gains[1:]:
        #    ads.gain = gain
        #    print("ads.gain= ", ads.gain)
        #    print(' | {:5} {:5.3f}'.format(chan.value, chan.voltage), end='')
        #print()
        #uart_server.write("testing/")
        #ads.gain = 2
        print("adc count= ", adc_cnt)
        # calcuate current thru SSA-100
        i_SSA = (adc_cnt/32767) * 170.7
        print ("SSA-100 current = ", i_SSA)
        print(' count= {:5} voltage = {:5.3f}\n'.format(adc_cnt, adc_volt))
        #uart_server.write('{},{}\n'.format(chan.value, small))
        #uart_server.write(b'55uuhh\n')
        time.sleep(1.0)
        # send adc count and voltage
        uart_server.write('ADC count={:5} value={:5.3f} volts\n'.format(adc_cnt, adc_volt))
        time.sleep(0.1)
        # send elapsed time and current
        uart_server.write('elapsed time={:5.0f} value={:5.1f} amps\n'.format(now, i_SSA))
        time.sleep(0.5)

    # Disconnected
    print("DISCONNECTED")