#
#    WORK IN PROGRESS
#
# main.py - controlling LCD ili9341
# Gets data recieve by 4-line Serial protocol (Series II)
#
# TODO: Realize fast screen refresh

import os
import struct

import pyb, micropython
from pyb import SPI, Pin

micropython.alloc_emergency_exception_buf(100)

rate = 168000000

spi = SPI(1, SPI.MASTER, baudrate=rate, polarity=1, phase=1)
csx = Pin('X4', Pin.OUT_PP)    # CSX Pin
dcx = Pin('X5', Pin.OUT_PP)    # D/Cx Pin
rst = Pin('X3', Pin.OUT_PP)    # Reset Pin


# Color definitions.
#     RGB 16-bit Color (R:5-bit; G:6-bit; B:5-bit)
BLACK16       = [0,  0,  0 ]        #   0,   0,   0
NAVY16        = [0,  0,  15]        #   0,   0, 128
DARKGREEN16   = [0,  31, 0 ]        #   0, 128,   0
DARKCYAN16    = [0,  31, 15]        #   0, 128, 128
MAROON16      = [15, 0,  0 ]        # 128,   0,   0
PURPLE16      = [15, 0,  15]        # 128,   0, 128
OLIVE16       = [15, 31, 0 ]        # 128, 128,   0
LIGHTGREY16   = [23, 47, 23]        # 192, 192, 192
DARKGREY16    = [15, 31, 15]        # 128, 128, 128
BLUE16        = [0,  0,  31]        #   0,   0, 255
GREEN16       = [0,  63, 0 ]        #   0, 255,   0
CYAN16        = [0,  63, 31]        #   0, 255, 255
RED16         = [31, 0,  0 ]        # 255,   0,   0
MAGENTA16     = [31, 0,  31]        # 255,   0, 255
YELLOW16      = [31, 63, 0 ]        # 255, 255,   0
WHITE16       = [31, 63, 31]        # 255, 255, 255
ORANGE16      = [31, 39, 0 ]        # 255, 165,   0
GREENYELLOW16 = [18, 63, 4 ]        # 173, 255,  47

#     RGB 18-bit Color (R:6-bit; G:6-bit; B:6-bit)
BLACK18       = [0,  0,  0 ]        #   0,   0,   0
NAVY18        = [0,  0,  31]        #   0,   0, 128
DARKGREEN18   = [0,  31, 0 ]        #   0, 128,   0
DARKCYAN18    = [0,  31, 31]        #   0, 128, 128
MAROON18      = [31, 0,  0 ]        # 128,   0,   0
PURPLE18      = [31, 0,  31]        # 128,   0, 128
OLIVE18       = [31, 31, 0 ]        # 128, 128,   0
LIGHTGREY18   = [39, 47, 39]        # 192, 192, 192
DARKGREY18    = [31, 31, 31]        # 128, 128, 128
BLUE18        = [0,  0,  63]        #   0,   0, 255
GREEN18       = [0,  63, 0 ]        #   0, 255,   0
CYAN18        = [0,  63, 63]        #   0, 255, 255
RED18         = [63, 0,  0 ]        # 255,   0,   0
MAGENTA18     = [63, 0,  63]        # 255,   0, 255
YELLOW18      = [63, 63, 0 ]        # 255, 255,   0
WHITE18       = [63, 63, 63]        # 255, 255, 255
ORANGE18      = [63, 39, 0 ]        # 255, 165,   0
GREENYELLOW18 = [36, 63, 8 ]        # 173, 255,  47

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
    # | MY=0 | MX=0 | MV=0 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
    lcd_write_data(0x48)

    lcd_write_cmd(PIXFMT)   # Pixel format set
    lcd_write_data(0x66)    # 18-bit/pixel
    #lcd_write_data(0x55)    # 16-bit/pixel

    lcd_write_cmd(FRMCTR1)  # Frame rate control (in normal mode)
    lcd_write_data(0x01)    # fosc/2
    lcd_write_data(0x10)    # 112Hz (Default)
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

def lcd_test():
    for y in range(TFTHEIGHT):
        for x in range(TFTWIDTH):
            if (y > 279): lcd_write_color18(WHITE18)
            elif (y > 239): lcd_write_color18(PURPLE18)
            elif (y > 199): lcd_write_color18(BLUE18)
            elif (y > 159): lcd_write_color18(CYAN18)
            elif (y > 119): lcd_write_color18(GREEN18)
            elif (y > 79): lcd_write_color18(YELLOW18)
            elif (y > 39): lcd_write_color18(ORANGE18)
            else: lcd_write_color18(RED18)

def lcd_random_test():
    colors = [
        BLACK18,    NAVY18,    DARKGREEN18,  DARKCYAN18,
        MAROON18,   PURPLE18,  OLIVE18,      LIGHTGREY18,
        DARKGREY18, BLUE18,    GREEN18,      CYAN18,
        RED18,      MAGENTA18, YELLOW18,     WHITE18,
        ORANGE18,   GREENYELLOW18
        ]
    screen = TFTWIDTH*5
    j = 0
    for i in range((320*240)/screen):
        j = struct.unpack('<B', os.urandom(1))[0]//15
        lcd_draw_pixels(0, i*5, [colors[j] for c in range(screen)])

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

def lcd_write_color16(color):
    R, G, B = color
    csx.low()
    dcx.high()
    word = struct.pack('<BB', (R<<3) | (G>>3), (G<<5) | (B))
    spi.send(word)
    csx.high()
    dcx.low()

def lcd_write_color18(color):
    R, G, B = color
    csx.low()
    dcx.high()
    word = struct.pack('<BBB', (R<<2), (G<<2), (B<<2))
    spi.send(word)
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

def lcd_draw_pixel(x, y, color, rgb=18):
    lcd_set_window(x, x, y, y)
    if rgb == 18:
        lcd_write_color18(color)
    elif rgb == 16:
        lcd_write_color16(color)

def lcd_draw_pixels(x, y, data):
    i = 0
    lcd_set_window(x, TFTWIDTH-1, y, TFTHEIGHT-1)
    while i < len(data):
        lcd_write_color18(data[i])
        i+=1

def lcd_draw_Vline(x, y0, y1, color):
    lcd_set_window(x, x, y0, y1)
    for line in range(y1-y0):
        lcd_write_color18(color)

def lcd_draw_Hline(x, y, length, color):
    i = 0
    lcd_set_window(x, x+length, y, y)
    while i < length:
        lcd_write_color18(color)
        i+=1

def lcd_fill_screen(color, padding):
    x = padding
    lcd_set_window(padding, TFTWIDTH-padding, padding, TFTHEIGHT-padding)
    while x < ((TFTWIDTH-padding)*(TFTHEIGHT-padding)):
        lcd_write_color18(color)
        x+=1

# TEST CODE

lcd_init()

lcd_random_test()
lcd_set_window(0, TFTWIDTH-0, 0, TFTHEIGHT-0)
lcd_test()

x0 = y0 = 10
x1 = y1 = 310

lcd_fill_screen(GREENYELLOW18, 10)

lcd_draw_Vline(x0, y0, y1, BLACK18)
lcd_draw_Vline(x0+220, y0, y1, BLACK18)
lcd_draw_Vline(x0+219, y0, y1, BLACK18)
lcd_draw_Hline(x0, y0, TFTWIDTH-20, BLACK18)
lcd_draw_Hline(x0, y1, TFTWIDTH-20, BLACK18)
lcd_draw_Hline(x0, y0+1, TFTWIDTH-20, BLACK18)
