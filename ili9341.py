#
#    WORK IN PROGRESS
#
# main.py - controlling LCD ili9341
# Gets data transfer by 4-line Serial protocol (Series II)
#

import os
import struct

import pyb, micropython
from pyb import SPI, Pin

micropython.alloc_emergency_exception_buf(100)

rate = 32000000

spi = SPI(1, SPI.MASTER, baudrate=rate, polarity=1, phase=1)
csx = Pin('X4', Pin.OUT_PP)    # CSX Pin
dcx = Pin('X5', Pin.OUT_PP)    # D/Cx Pin
rst = Pin('X3', Pin.OUT_PP)    # Reset Pin


# Color definitions.
#     RGB 16-bit Color (R:5-bit; G:6-bit; B:5-bit)
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
RDID1      = 0xDA
RDID2      = 0xDB
RDID3      = 0xDC
RDID4      = 0xDD
#    LCD settings registers:
SLPIN      = 0x10    # Enter Sleep Mode (page 100)
SLPOUT     = 0x11    # Sleep Out (page 101)

PTLON      = 0x12    # Partial Mode ON (page 103)
NORON      = 0x13    # Partial Mode OFF

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

def lcd_write(word, dc, recv):
    dcs = ['cmd', 'data']

    DCX = dcs.index(dc) if dc in dcs else None

    csx.low()
    dcx.value(DCX)
    if recv:
        recv = bytearray(5)
        data = spi.send_recv(struct.pack('<BI', word), recv=recv)
    else:
        spi.send(word)

    csx.high()

def lcd_write_cmd(word, recv=None):
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

def lcd_init():
    rst.high()              #
    pyb.delay(1)            #
    rst.low()               #    RESET LCD SCREEN
    pyb.delay(1)            #
    rst.high()              #

    lcd_write_cmd(LCDOFF)   # Display OFF
    pyb.delay(10)

    lcd_write_cmd(SWRESET)  # Reset SW
    pyb.delay(50)
    lcd_write_cmd(MADCTL)   # Memory Access Control
    # | MY=0 | MX=1 | MV=0 | ML=0 | BGR=0 | MH=0 | 0 | 0 |
    lcd_write_data(0x48)

    lcd_write_cmd(PIXFMT)   # Pixel format set
    #lcd_write_data(0x66)    # 18-bit/pixel
    lcd_write_data(0x55)    # 16-bit/pixel

    lcd_write_cmd(FRMCTR1)  # Frame rate control (in normal mode)
    lcd_write_data(0x00)    # fosc/2
    lcd_write_data(0x10)    # 112Hz
    #lcd_write_data(0x1B)    # 70Hz (Default)

    lcd_write_cmd(GAMMASET)
    lcd_write_data(0x01)

    lcd_write_cmd(0xb7)     # Entry mode set
    lcd_write_data(0x07)

    lcd_write_cmd(PTLON)    # Partial mode ON

    #lcd_write_cmd(DFUNCTR)  # Display function control
    #lcd_write_data(0x0a)
    #lcd_write_data(0x82)
    #lcd_write_data(0x27)
    #lcd_write_data(0x00)

    lcd_write_cmd(SLPOUT)    # sleep mode OFF
    pyb.delay(100)
    lcd_write_cmd(LCDON)
    pyb.delay(100)
    lcd_write_cmd(RAMWR)

def get_wordflow_4Xmono(color, pixels):
    R, G, B = color
    fmt = '>{0}Q'.format(pixels)
    pixel = (R<<11) | (G<<5) | B
    colorflow = [pixel<<(16*3) | pixel<<(16*2) | pixel<<16 | pixel] * pixels

    if pixels % 4:
        mod = pixels % 4
        fmt + '{0}'.format('H' * mod)
        for i in range(mod):
            colorflow.append(pixel)

    word = struct.pack(fmt, *colorflow)
    return word

def lcd_test():
    colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE]
    pixels = TFTWIDTH*10
    for i in range(TFTHEIGHT//40):
        word = get_wordflow_4Xmono(colors[i], pixels)
        lcd_write_data(word)

def lcd_random_test():
    colors = [
        BLACK,    NAVY,    DARKGREEN,  DARKCYAN,
        MAROON,   PURPLE,  OLIVE,      LIGHTGREY,
        DARKGREY, BLUE,    GREEN,      CYAN,
        RED,      MAGENTA, YELLOW,     WHITE,
        ORANGE,   GREENYELLOW
        ]
    pixels = TFTWIDTH*5
    j = 0
    for i in range(TFTHEIGHT/20):
        j = struct.unpack('<B', os.urandom(1))[0]//15
        word = get_wordflow_4Xmono(colors[j], pixels)
        lcd_write_data(word)

def lcd_draw_Vline(x, y, length, color, width=1):
    lcd_set_window(x, x+(width-1), y, length)
    word = get_wordflow_4Xmono(color, length)
    for i in range(width):
        lcd_write_data(word)

def lcd_draw_Hline(x, y, length, color, width=1):
    lcd_set_window(x, length, y, y+(width-1))
    word = get_wordflow_4Xmono(color, length)
    for i in range(width):
        lcd_write_data(word)

def lcd_draw_rect(x, y, width, height, color, border=1, fillcolor=None):
    if border:
        if border > height//2:
            raise ValueError ("too high border value")
            X, Y = x, y
        for i in range(2):
            Y = y+height-(border-1) if i == 1 else y
            X = x if i == 1 else x
            lcd_draw_Hline(X, Y, x+width, color, border)

            Y = y+(border-1) if i == 1 else y
            X = x+width-(border-1) if i == 1 else x
            lcd_draw_Vline(X, Y, y+height, color, border)
    else:
        fillcolor = color

    if fillcolor:
        xsum = x+border
        ysum = y+border
        lcd_set_window(xsum, xsum+width-(border*2), ysum, ysum+height-(border*2))
        pixels = (width-(border*2))
        word = get_wordflow_4Xmono(fillcolor, pixels)
        x=0
        rows = (height-(border*2)+width+border*2)//4
        if rows < 1: rows = 1
        while x < (rows):
            lcd_write_data(word)
            x+=1

def lcd_fill_monocolor(color, margin=0):
    lcd_draw_rect(margin, margin, TFTWIDTH, TFTHEIGHT, color, border=0, fillcolor=color)


# TEST CODE


lcd_init()

lcd_random_test()
lcd_test()
