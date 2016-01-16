# main.py - controlling LCD ili9341

import struct

import pyb, micropython
from pyb import SPI, Pin, ExtInt

micropython.alloc_emergency_exception_buf(100)

pyb.freq(64000000)

ILI9341_TFTWIDTH  = 240
ILI9341_TFTHEIGHT = 320

ILI9341_NOP       = 0x00
ILI9341_SWRESET   = 0x01
ILI9341_RDDID     = 0x04
ILI9341_RDDST     = 0x09

ILI9341_SLPIN     = 0x10
ILI9341_SLPOUT    = 0x11
ILI9341_PTLON     = 0x12
ILI9341_NORON     = 0x13

ILI9341_RDMODE    = 0x0A
ILI9341_RDMADCTL  = 0x0B
ILI9341_RDPIXFMT  = 0x0C
ILI9341_RDIMGFMT  = 0x0D
ILI9341_RDSELFDIAG = 0x0F

ILI9341_INVOFF     = 0x20
ILI9341_INVON      = 0x21
ILI9341_GAMMASET   = 0x26
ILI9341_DISPOFF    = 0x28
ILI9341_DISPON     = 0x29

ILI9341_CASET      = 0x2A
ILI9341_PASET      = 0x2B
ILI9341_RAMWR      = 0x2C
ILI9341_RAMRD      = 0x2E

ILI9341_PTLAR      = 0x30
ILI9341_MADCTL     = 0x36
ILI9341_PIXFMT     = 0x3A

ILI9341_FRMCTR1    = 0xB1
ILI9341_FRMCTR2    = 0xB2
ILI9341_FRMCTR3    = 0xB3
ILI9341_INVCTR     = 0xB4
ILI9341_DFUNCTR    = 0xB6

ILI9341_PWCTR1     = 0xC0
ILI9341_PWCTR2     = 0xC1
ILI9341_PWCTR3     = 0xC2
ILI9341_PWCTR4     = 0xC3
ILI9341_PWCTR5     = 0xC4
ILI9341_VMCTR1     = 0xC5
ILI9341_VMCTR2     = 0xC7

ILI9341_RDID1      = 0xDA
ILI9341_RDID2      = 0xDB
ILI9341_RDID3      = 0xDC
ILI9341_RDID4      = 0xDD

ILI9341_GMCTRP1    = 0xE0
ILI9341_GMCTRN1    = 0xE1
#ILI9341_PWCTR6     =  0xFC



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

spi = SPI(1, SPI.MASTER, baudrate=32000, polarity=0, phase=1, firstbit=SPI.MSB)
csx = Pin('X4', Pin.OUT_PP)

def lcd_write(word, dc):
    dcs = ['comm', 'data']
    shift = 8 if len(bin(word)[2:]) <= 8 else 0

    if dc in dcs: DCX = dcs.index(dc)
    else: DCX = None
    csx.low()
    spi.send(struct.pack('<H', DCX|(word<<shift)))
    csx.high()


def lcd_write_comm(word):
    lcd_write(word, 'comm')

def lcd_write_data(word):
    lcd_write(word, 'data')

def Lcd_Init():
    pass

while True:
    lcd_write_comm(0xB4)
    lcd_write_data(0xB4)
