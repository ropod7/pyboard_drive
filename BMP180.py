# BMP180.py -- controlling barometer

import struct, math

import pyb, micropython
from pyb import I2C, Switch

micropython.alloc_emergency_exception_buf(100)

i2c = I2C(2, I2C.MASTER, baudrate=3000)
sw = Switch()

# oversampling setting (short 0..3)
oss = 3

# sea level Zero point in hPa
PaZero = 1013.25

def change_format(n, tp):
    types = dict(
            long = '<l',
            ulong = '<L',
            ushort = '<H',
            short = '<h',
        )
    formatted = struct.unpack(types[tp], struct.pack(types[tp], n))[0]
    return formatted

def get_I2C_calib(msb, lsb, unsigned=False):
    # 'H' = unsigned short, 'h' = signed short
    tp = '<H' if unsigned else '<h'
    MSB = struct.unpack(tp, i2c.mem_read(1, 0x77, msb))[0]
    LSB = struct.unpack(tp, i2c.mem_read(1, 0x77, lsb))[0]
    tp = 'ushort' if unsigned else 'short'
    data = change_format((MSB<<8 | LSB), tp)

    return data

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
        i2c.mem_write(0x2E, 0x77, 0xF4)
        pyb.delay(4)

        MSB = struct.unpack("<h", i2c.mem_read(1, 0x77, 0xF6))[0]
        LSB = struct.unpack("<h", i2c.mem_read(1, 0x77, 0xF7))[0]

        UT += (MSB*2**8) | LSB

    return int(UT/3)

def calc_true_Temp():
    UT = read_BMP180_temp()
    x1 = (UT - data['AC6']) * data['AC5'] / 2**15    # data>>15 == data / 2**15
    x1 = int(x1)
    x2 = (data['MC'] * 2**11) / (x1 + data['MD'])    # data<<11 == data * 2**11
    x2 = int(x2)
    b5 = x1 + x2
    #print(x1, x2, UT)

    tempC = round(((b5 + 8) / pow(2, 4)) * 0.1, 1)
    return tempC, b5

def read_BMP180_pressure():
    data = 0x34 + (oss<<6)
    UP = 0
    for i in range(3):
        i2c.mem_write(data, 0x77, 0xF4)
        pyb.delay(2 + (3<<oss))

        MSB = struct.unpack("<L", i2c.mem_read(1, 0x77, 0xF6))[0]
        LSB = struct.unpack("<L", i2c.mem_read(1, 0x77, 0xF7))[0]
        XLSB = struct.unpack("<L", i2c.mem_read(1, 0x77, 0xF8))[0]
        UP += (MSB*2**16 | LSB*2**8 | XLSB) >> (8 - oss)

    return int(UP/3)

def calc_true_pressure():
    UP = read_BMP180_pressure()
    b5 = int(calc_true_Temp()[1])
    b6 = b5 - 4000

    # calculate b3
    x1 = (b6 * b6) / 2**12
    x1 *= data['B2']
    x1 /= 2**11
    x1 = int(x1)
    x2 = int((data['AC2'] * b6) / 2**11)
    x3 = int(x1 + x2)
    b3 = (((data['AC1'] * 4 + x3) * 2 ** oss) + 2) / 4
    #print(b6, b5, x1, x2, x3, b3)

    # calculate b4
    x1 = (data['AC3'] * b6) / 2**13
    x2 = (data['B1'] *((b6 * b6) / 2**12)) / 2**16
    x3 = ((x1 + x2) + 2) / 4
    ulong_n = change_format(int(x3) + 32768, 'ulong')
    b4 = data['AC4'] * (ulong_n) / 2**15
    b4 = change_format(int(b4), 'ulong')

    ulong_UP = change_format(UP, 'ulong')
    b7 = (ulong_UP - b3) * (50000>>oss)
    b7 = change_format(int(b7), 'ulong')

    if b7 < 0x80000000:
        p = (b7*2) / b4
    else:
        p = int(b7 / b4) * 2

    x1 = p / 2**8
    x1 *= x1
    x1 = (x1 * 3038) / 2**16
    x2 = (-7357*p) / 2**16

    # pressure in Pa
    pressure = p + (x1 + x2 + 3791)  / 2**4

    return pressure

def calc_meters_above_Sea_Level():
    Pa = calc_true_pressure()
    hPa = round(Pa/100, 2)

    altitude = 44330 * (1 - math.pow((hPa/PaZero), (1/5.255)) )

    return round(altitude, 1), hPa

def print_temp_meters():
    t = calc_true_Temp()[0]
    altitude, hPa = calc_meters_above_Sea_Level()
    string = """
    temperature = {0}C
    altitude = {1}m
    pressure = {2}hPa
    \n\n\n
    """
    return string.format(t, altitude, hPa)

data = read_E2PROM_regs()

#print(print_temp_meters())

while True:
    while sw():
        print(print_temp_meters())
        pyb.delay(500)
