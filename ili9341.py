#
#    WORK IN PROGRESS
#
# main.py - controlling LCD ili9341
# Gets data recieve by 4-line Serial protocol (Series II)
#
# TODO: Realize fast screen graphics update

import struct

import pyb, micropython
from pyb import SPI, Pin

micropython.alloc_emergency_exception_buf(100)

rate = 800000

spi = SPI(1, SPI.MASTER, baudrate=rate, polarity=1, phase=1)
csx = Pin('X4', Pin.OUT_PP)
dcx = Pin('X5', Pin.OUT_PP)
rst = Pin('X3', Pin.OUT_PP)

# Color definitions
BLACK       = [0,  0,  0 ]        #   0,   0,   0
NAVY        = [0,  0,  15]        #   0,   0, 128
DARKGREEN   = [0,  31, 0 ]        #   0, 128,   0
DARKCYAN    = [0,  31, 15]        #   0, 128, 128
MAROON      = [15, 0,  0 ]        # 128,   0,   0
PURPLE      = [15, 0,  15]        # 128,   0, 128
OLIVE       = [15, 31, 0 ]        # 128, 128,   0
LIGHTGREY   = [23, 47, 23]        # 192, 192, 192
DARKGREY    = [15, 31, 15]        # 128, 128, 128
BLUE        = [0,  0,  31]        #   0,   0, 255
GREEN       = [0,  63, 0 ]        #   0, 255,   0
CYAN        = [0,  63, 31]        #   0, 255, 255
RED         = [31, 0,  0 ]        # 255,   0,   0
MAGENTA     = [31, 0,  31]        # 255,   0, 255
YELLOW      = [31, 63, 0 ]        # 255, 255,   0
WHITE       = [31, 63, 31]        # 255, 255, 255
ORANGE      = [31, 39, 0 ]        # 255, 165,   0
GREENYELLOW = [18, 63, 4 ]        # 173, 255,  47

TFTWIDTH  = 240
TFTHEIGHT = 320

# LCD control registers
NOP        = 0x00
SWRESET    = 0x01    # Software Reset (page 90)
#     LCD Read status registers
RDDID      = 0x04    # Read display identification 24-bit information (page 91)
RDDST      = 0x09    # Read Display Status 32-bit (page 92)
RDDPM      = 0x0A    # Read Display Power Mode 8-bit (page 94)
RDDMADCTL  = 0x0B    # Read Display MADCTL 8-bit (page 95)
RDPIXFMT   = 0x0C    # Read Display Pixel Format 8-bit (page 96)
RDDIM      = 0x0D    # Read Display Image Format 3-bit (page 97)
RDDSM      = 0x0E    # Read Display Signal Mode 8-bit (page 98)
RDDSDR     = 0x0F    # Read Display Self-Diagnostic Result 8-bit (page 99)

SLPIN      = 0x10    # Enter Sleep Mode (page 100)

RDID1      = 0xDA
RDID2      = 0xDB
RDID3      = 0xDC
RDID4      = 0xDD

SLPOUT     = 0x11
PTLON      = 0x12
NORON      = 0x13

INVOFF     = 0x20
INVON      = 0x21
GAMMASET   = 0x26
LCDOFF     = 0x28
LCDON      = 0x29

CASET      = 0x2A
PASET      = 0x2B
RAMWR      = 0x2C
RGBSET     = 0x2D
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

GMCTRP1    = 0xE0
GMCTRN1    = 0xE1
#PWCTR6     =  0xFC

def lcd_init():
    rst.low()
    lcd_write_cmd(LCDOFF)              # Display OFF
    pyb.delay(10)

    lcd_write_cmd(SWRESET)             # Reset SW
    pyb.delay(50)
    rst.high()
    lcd_write_cmd(MADCTL)              # Memory Access Control
    lcd_write_data(0)

    lcd_write_cmd(PIXFMT)    # Pixel format set
    lcd_write_data(0x55)

    lcd_write_cmd(FRMCTR1)    # Frame control (in normal mode)
    lcd_write_data(0x00)
    lcd_write_data(0x1B)

    lcd_write_cmd(GAMMASET)
    lcd_write_data(0x01)

    lcd_write_cmd(CASET)    # Column Address Set
    lcd_write_data(0x00)
    lcd_write_data(0x00)
    lcd_write_data(0x00)
    lcd_write_data(0xEF)

    lcd_write_cmd(PASET)    # Page Address Set
    lcd_write_data(0x00)
    lcd_write_data(0x00)
    lcd_write_data(0x01)
    lcd_write_data(0x3F)

    lcd_write_cmd(0xb7)     # Entry mode set
    lcd_write_data(0x07)

    lcd_write_cmd(DFUNCTR)
    lcd_write_data(0x0a)
    lcd_write_data(0x82)
    lcd_write_data(0x27)
    lcd_write_data(0x00)

    lcd_write_cmd(SLPOUT)
    pyb.delay(100)
    lcd_write_cmd(LCDON)
    pyb.delay(100)
    lcd_write_cmd(RAMWR)

def lcdTest():
    for y in range(320):
        for x in range(240):
            if (y > 279): lcd_write_color(LIGHTGREY)
            elif (y > 239): lcd_write_color(OLIVE)
            elif (y > 199): lcd_write_color(DARKCYAN)
            elif (y > 159): lcd_write_color(ORANGE)
            elif (y > 119): lcd_write_color(MAROON)
            elif (y > 79): lcd_write_color(PURPLE)
            elif (y > 39): lcd_write_color(NAVY)
            else: lcd_write_color(DARKGREEN)

def lcd_write(word, dc, recv):
    dcs = ['cmd', 'data']

    if dc in dcs: DCX = dcs.index(dc)
    else: DCX = None

    csx.low()
    dcx.value(DCX)
    if recv:
        recv = bytearray(5)
        data = spi.send_recv(struct.pack('<BI', word), recv=recv)
    else:
        spi.send(word)

    csx.high()

def lcd_write_color(color):
    R, G, B = color
    csx.low()
    dcx.high()
    spi.send(struct.pack('<BB', (B<<3) | (G>>3), (G<<5) | (R)))
    csx.high()
    dcx.low()

def lcd_write_cmd(word=NOP, recv=None):
    data = lcd_write(word, 'cmd', recv)
    return data

def lcd_write_data(word):
    lcd_write(word, 'data', recv=None)

def lcd_set_window(x0, y0, x1, y1):
    lcd_write_cmd(CASET)                # Column Address Set
    lcd_write_data((x0>>8) & 0xFF)
    lcd_write_data(x0 & 0xFF)
    lcd_write_data((y0>>8) & 0xFF)
    lcd_write_data(y0 & 0xFF)
    lcd_write_cmd(PASET)                # Page Address Set
    lcd_write_data((x1>>8) & 0xFF)
    lcd_write_data(x1 & 0xFF)
    lcd_write_data((y1>>8) & 0xFF)
    lcd_write_data(y1 & 0xFF)
    lcd_write_cmd(RAMWR)                # Memory Write

def lcd_draw_pixel(x, y, color):
    lcd_set_window(x, x, y, y)
    lcd_write_color(color)

def lcd_draw_Vline(x, y0, y1, color):
    for line in range(y0, y1):
        lcd_draw_pixel(x, line, color)

lcd_init()
#lcdTest()
x = y0 = 10
y1 = 310

lcd_draw_Vline(x, y0, y1, YELLOW)
lcd_draw_Vline(x+220, y0, y1, YELLOW)
