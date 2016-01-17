#
#    WORK IN PROGRESS
#
# main.py - controlling LCD ili9341
# trying to connect by 3-Line method as shown in datasheet
# where using | SDA | SCL | CSX | lines only
# still have not hardware feedback

import struct

import pyb, micropython
from pyb import SPI, Pin

micropython.alloc_emergency_exception_buf(100)

# Color definitions
ILI9341_BLACK       = 0x0000      #   0,   0,   0
ILI9341_NAVY        = 0x000F      #   0,   0, 128
ILI9341_DARKGREEN   = 0x03E0      #   0, 128,   0
ILI9341_DARKCYAN    = 0x03EF      #   0, 128, 128
ILI9341_MAROON      = 0x7800      # 128,   0,   0
ILI9341_PURPLE      = 0x780F      # 128,   0, 128
ILI9341_OLIVE       = 0x7BE0      # 128, 128,   0
ILI9341_LIGHTGREY   = 0xC618      # 192, 192, 192
ILI9341_DARKGREY    = 0x7BEF      # 128, 128, 128
ILI9341_BLUE        = 0x001F      #   0,   0, 255
ILI9341_GREEN       = 0x07E0      #   0, 255,   0
ILI9341_CYAN        = 0x07FF      #   0, 255, 255
ILI9341_RED         = 0xF800      # 255,   0,   0
ILI9341_MAGENTA     = 0xF81F      # 255,   0, 255
ILI9341_YELLOW      = 0xFFE0      # 255, 255,   0
ILI9341_WHITE       = 0xFFFF      # 255, 255, 255
ILI9341_ORANGE      = 0xFD20      # 255, 165,   0
ILI9341_GREENYELLOW = 0xAFE5      # 173, 255,  47
ILI9341_PINK        = 0xF81F

TFTWIDTH  = 240
TFTHEIGHT = 320

# LCD control registers
SWRESET   = 0x01    # Software Reset (page 90)
RDDID     = 0x04    # Read display identification information (page 91)
RDDST     = 0x09    # Read Display Status (page 92)
RDMODE    = 0x0A    # Read Display Power Mode (page 94)

SLPIN     = 0x10
SLPOUT    = 0x11
PTLON     = 0x12
NORON     = 0x13

RDMADCTL  = 0x0B
RDPIXFMT  = 0x0C
RDIMGFMT  = 0x0D
RDSELFDIAG = 0x0F

INVOFF     = 0x20
INVON      = 0x21
GAMMASET   = 0x26
DISPOFF    = 0x28
DISPON     = 0x29

CASET      = 0x2A
PASET      = 0x2B
RAMWR      = 0x2C
RAMRD      = 0x2E

PTLAR      = 0x30
MADCTL     = 0x36
PIXFMT     = 0x3A

FRMCTR1    = 0xB1
FRMCTR2    = 0xB2
FRMCTR3    = 0xB3
INVCTR     = 0xB4
DFUNCTR    = 0xB6

PWCTR1     = 0xC0
PWCTR2     = 0xC1
PWCTR3     = 0xC2
PWCTR4     = 0xC3
PWCTR5     = 0xC4
VMCTR1     = 0xC5
VMCTR2     = 0xC7

RDID1      = 0xDA
RDID2      = 0xDB
RDID3      = 0xDC
RDID4      = 0xDD

GMCTRP1    = 0xE0
GMCTRN1    = 0xE1
#PWCTR6     =  0xFC

spi = SPI(1, SPI.MASTER, baudrate=1, polarity=0, phase=1, firstbit=SPI.MSB)
csx = Pin('X4', Pin.OUT_PP)
dcx = Pin('X5', Pin.OUT_PP)

def lcd_write(word, dc, recv=False):
    dcs = ['comm', 'data']
    shift = 24 if len(bin(word)[2:]) <= 8 else 0

    if dc in dcs: DCX = dcs.index(dc)
    else: DCX = None
    csx.low()
    dcx.value(DCX)
    if recv:
        recv = bytearray(4)
        data = spi.send_recv(struct.pack('<I', word<<shift), recv=recv, timeout=5000)
        csx.high()
        return struct.unpack('<H', data)[0]
    else:
        spi.send(word, timeout=5000)
        csx.high()


def lcd_write_comm(word, recv=False):
    data = lcd_write(word, 'comm', recv)
    return data

def lcd_write_data(word, recv=False):
    data = lcd_write(word, 'data', recv)
    return data

while True:
    lcd_write_comm(SWRESET)
    print(lcd_write_comm(RDDID, recv=True))
    lcd_write_data(0x01, recv=True)
