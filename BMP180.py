# BMP180.py -- controlling barometer BMP180

import struct

import pyb, micropython
from pyb import I2C, Switch

micropython.alloc_emergency_exception_buf(100)

i2c = I2C(2, I2C.MASTER, baudrate=3000)
sw = Switch()

# oversampling setting (short 0..3)
oss = 3

# standard sea level at Zero point in hPa
#hPaZero = 1013.25

def get_I2C_calib(msb, lsb, unsigned=False):
    # 'H' = unsigned short, 'h' = signed short
    tp = '<H' if unsigned else '<h'
    MSB = struct.unpack(tp, i2c.mem_read(1, 0x77, msb))[0]
    LSB = struct.unpack(tp, i2c.mem_read(1, 0x77, lsb))[0]
    data = struct.unpack(tp, struct.pack(tp, (MSB<<8 | LSB)))[0]

    return data

# function returns calibration data
def read_E2PROM_regs():
    data = dict()
    data['AC1'] = get_I2C_calib(0xAA, 0xAB)
    data['AC2'] = get_I2C_calib(0xAC, 0xAD)
    data['AC3'] = get_I2C_calib(0xAE, 0xAF)
    data['AC4'] = get_I2C_calib(0xB0, 0xB1, unsigned=True)
    data['AC5'] = get_I2C_calib(0xB2, 0xB3, unsigned=True)
    data['AC6'] = get_I2C_calib(0xB4, 0xB5, unsigned=True)
    data['B1'] = get_I2C_calib(0xB6, 0xB7)
    data['B2'] = get_I2C_calib(0xB8, 0xB9)
    data['MB'] = get_I2C_calib(0xBA, 0xBB)
    data['MC'] = get_I2C_calib(0xBC, 0xBD)
    data['MD'] = get_I2C_calib(0xBE, 0xBF)

    return data

def read_BMP180_temp():
    UT = 0
    for i in range(3):
        # writing read temp register 0x2E
        i2c.mem_write(0x2E, 0x77, 0xF4)
        pyb.udelay(4500)

        MSB = struct.unpack("<h", i2c.mem_read(1, 0x77, 0xF6))[0]
        LSB = struct.unpack("<h", i2c.mem_read(1, 0x77, 0xF7))[0]

        UT += (MSB<<8) | LSB

    return int(UT/3)

def read_BMP180_pressure():
    data = 0x34 + (oss<<6)
    UP = 0
    for i in range(3):
        # writing read pressure register
        # with oversampling reg setting: 0x34 + (oss<<6)
        i2c.mem_write(data, 0x77, 0xF4)
        pyb.delay(2 + (3<<oss))

        MSB = struct.unpack("<L", i2c.mem_read(1, 0x77, 0xF6))[0]
        LSB = struct.unpack("<L", i2c.mem_read(1, 0x77, 0xF7))[0]
        XLSB = struct.unpack("<L", i2c.mem_read(1, 0x77, 0xF8))[0]
        UP += (MSB<<16 | LSB<<8 | XLSB) >> (8 - oss)

    return UP/3

def calc_true_temp():
    UT = read_BMP180_temp()
    x1 = (UT - data['AC6']) * data['AC5']>>15    # data>>15 == data / 2**15
    x2 = (data['MC']<<11) / (x1 + data['MD'])    # data<<11 == data * 2**11
    b5 = x1 + x2

    tempC = round(((b5 + 8) / pow(2, 4)) * 0.1, 1)
    return tempC, b5

def calc_true_pressure():
    UP = read_BMP180_pressure()
    b5 = calc_true_temp()[1]
    b6 = b5 - 4000

    # calculate b3
    x1 = int(b6 * b6)>>12
    x1 *= data['B2']
    x1 >>= 11
    x2 = int(data['AC2'] * b6)>>11
    x3 = x1 + x2
    b3 = (((data['AC1'] * 4 + x3) * 2 ** oss) + 2) / 4

    # calculate b4
    x1 = int(data['AC3'] * b6)>>13
    x2 = (data['B1'] *(int(b6 * b6)>>12))>>16
    x3 = ((x1 + x2) + 2)>>2
    b4 = data['AC4'] * (x3 + 32768) / 2**15

    b7 = (UP - b3) * (50000>>oss)

    if b7 < 0x80000000:
        p = (b7*2) / b4
    else:
        p = (b7 / b4) * 2

    x1 = p / 2**8
    x1 *= x1
    x1 = (x1 * 3038) / 2**16
    x2 = (-7357 * p) / 2**16

    # pressure in Pa
    Pa = p + (x1 + x2 + 3791) / 2**4

    return Pa

def calc_meters_hpa():
    Pa = calc_true_pressure()
    hPa = Pa/100

    try:
        altitude = 44330 * (1 - (hPa/hPaZero)**(1/5.255) )
        return round(altitude, 1), round(hPa, 2)

    except NameError:
        return hPa

def print_temp_meters():
    t = calc_true_temp()[0]
    altitude, hPa = calc_meters_hpa()
    string = """
    temperature = {0}C
    Value from Zero point:
        altitude = {1}m
    pressure = {2}hPa
    \n
    """
    return string.format(t, altitude, hPa)

# get calibration regs
pyb.delay(500)
data = read_E2PROM_regs()
# get Zero point in hPa
hPaZero = calc_meters_hpa()

while True:
    while sw():
        print(print_temp_meters())
        pyb.delay(500)
