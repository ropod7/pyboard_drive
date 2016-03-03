#
#    WORK IN PROGRESS
#
# lcd.py - controlling TFT LCD ILI9341
# Data transfer using 4-line Serial protocol (Series II)
# 16-bit RGB Color (R:5-bit; G:6-bit; B:5-bit)
# About 30Hz monocolor screen refresh
#

import os
import struct
import math
import json
import array

import pyb, micropython
from pyb import SPI, Pin

from fonts import Arial_14
from registers import *

micropython.alloc_emergency_exception_buf(100)

imgcachedir = 'images/cache'
if 'cache' not in os.listdir('images'):
    try:
        os.mkdir(imgcachedir)
    except OSError: pass

rate = 42000000

spi = SPI(1, SPI.MASTER, baudrate=rate, polarity=1, phase=1, bits=8)
rst = Pin('X3', Pin.OUT_PP)    # Reset Pin
csx = Pin('X4', Pin.OUT_PP)    # CSX Pin
dcx = Pin('X5', Pin.OUT_PP)    # D/Cx Pin

# Color definitions.
#     RGB 16-bit Color (R:5-bit; G:6-bit; B:5-bit)
BLACK       = (0,  0,  0 )        #   0,   0,   0
NAVY        = (0,  0,  15)        #   0,   0, 128
DARKGREEN   = (0,  31, 0 )        #   0, 128,   0
DARKCYAN    = (0,  31, 15)        #   0, 128, 128
MAROON      = (15, 0,  0 )        # 128,   0,   0
PURPLE      = (15, 0,  15)        # 128,   0, 128
OLIVE       = (15, 31, 0 )        # 128, 128,   0
LIGHTGREY   = (23, 47, 23)        # 192, 192, 192
DARKGREY    = (15, 31, 15)        # 128, 128, 128
BLUE        = (0,  0,  31)        #   0,   0, 255
GREEN       = (0,  63, 0 )        #   0, 255,   0
CYAN        = (0,  63, 31)        #   0, 255, 255
RED         = (31, 0,  0 )        # 255,   0,   0
MAGENTA     = (31, 0,  31)        # 255,   0, 255
YELLOW      = (31, 63, 0 )        # 255, 255,   0
WHITE       = (31, 63, 31)        # 255, 255, 255
ORANGE      = (31, 39, 0 )        # 255, 165,   0
GREENYELLOW = (18, 63, 4 )        # 173, 255,  47

TFTWIDTH  = 240
TFTHEIGHT = 320

def lcd_reset():
    rst.low()               #
    pyb.delay(1)            #    RESET LCD SCREEN
    rst.high()              #

def lcd_write(word, dc, recv, recvsize=2):
    dcs = ['cmd', 'data']

    DCX = dcs.index(dc) if dc in dcs else None
    fmt = '>B{0}'.format('B' * recvsize)
    csx.low()
    dcx.value(DCX)
    if recv:
        recv = bytearray(1+recvsize)
        data = spi.send_recv(struct.pack(fmt, word), recv=recv)
        csx.high()
        return data

    spi.send(word)
    csx.high()

def lcd_write_cmd(word, recv=None):
    data = lcd_write(word, 'cmd', recv)
    return data

def lcd_write_data(word):
    lcd_write(word, 'data', recv=None)

def lcd_write_words(words):
    wordL = len(words)
    wordL = wordL if wordL > 1 else ""
    fmt = '>{0}B'.format(wordL)
    words = struct.pack(fmt, *words)
    lcd_write_data(words)

def set_char_orientation():
    lcd_write_cmd(MADCTL)   # Memory Access Control
    # | MY=1 | MX=1 | MV=1 | ML=1 | BGR=1 | MH=1 | 0 | 0 |
    lcd_write_data(0xE8)

def set_graph_orientation():
    lcd_write_cmd(MADCTL)   # Memory Access Control
    # | MY=0 | MX=1 | MV=0 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
    lcd_write_data(0x48)

def set_image_orientation():
    lcd_write_cmd(MADCTL)   # Memory Access Control
    # | MY=0 | MX=1 | MV=0 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
    lcd_write_data(0xC8)

def lcd_set_window(x0, y0, x1, y1):
    # Column Address Set
    lcd_write_cmd(CASET)
    lcd_write_words([(x0>>8) & 0xFF, x0 & 0xFF, (y0>>8) & 0xFF, y0 & 0xFF])
    # Page Address Set
    lcd_write_cmd(PASET)
    lcd_write_words([(x1>>8) & 0xFF, x1 & 0xFF, (y1>>8) & 0xFF, y1 & 0xFF])
    # Memory Write
    lcd_write_cmd(RAMWR)

@micropython.asm_thumb
def asm_get_charpos(r0, r1, r2):
    mul(r0, r1)
    adc(r0, r2)

def lcd_init():
    lcd_reset()

    lcd_write_cmd(LCDOFF)   # Display OFF
    pyb.delay(10)

    lcd_write_cmd(SWRESET)  # Reset SW
    pyb.delay(50)

    set_graph_orientation()

    lcd_write_cmd(PTLON)    # Partial mode ON

    lcd_write_cmd(PIXFMT)   # Pixel format set
    #lcd_write_data(0x66)    # 18-bit/pixel
    lcd_write_data(0x55)    # 16-bit/pixel

    lcd_write_cmd(GAMMASET)
    lcd_write_data(0x01)

    lcd_write_cmd(ETMOD)    # Entry mode set
    lcd_write_data(0x07)

    lcd_write_cmd(SLPOUT)   # sleep mode OFF
    pyb.delay(100)
    lcd_write_cmd(LCDON)
    pyb.delay(100)

    lcd_write_cmd(RAMWR)

def get_Npix_monoword(color, pixels=4):
    if color == WHITE:
        word = 0xFFFF
    elif color == BLACK:
        word = 0
    else:
        R, G, B = color
        word = (R<<11) | (G<<5) | B
    word = struct.pack('>H', word)
    if pixels == 4:
        word = word * 4
    return word

def lcd_test():
    colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE]
    pixels = 10 * TFTWIDTH
    for i in range(TFTHEIGHT//40):
        word = get_Npix_monoword(colors[i]) * pixels
        lcd_write_data(word)

def lcd_random_test():
    colors = [
        BLACK,    NAVY,    DARKGREEN,  DARKCYAN,
        MAROON,   PURPLE,  OLIVE,      LIGHTGREY,
        DARKGREY, BLUE,    GREEN,      CYAN,
        RED,      MAGENTA, YELLOW,     WHITE,
        ORANGE,   GREENYELLOW
        ]
    pixels = TFTWIDTH
    j = 0
    for i in range(TFTHEIGHT//4):
        j = struct.unpack('<B', os.urandom(1))[0]//15
        word = get_Npix_monoword(colors[j]) * pixels
        lcd_write_data(word)

def lcd_chars_test(color, font=Arial_14, bgcolor=WHITE, scale=1):
    scale = 2 if scale > 1 else 1
    x = y = 7 * scale
    for i in range(33, 128):
        chrwidth = len(font['ch' + str(i)])
        cont = False if i == 127 else True
        lcd_print_char(chr(i), x, y, color, font, bgcolor=bgcolor, cont=cont, scale=scale)
        x += asm_get_charpos(chrwidth, scale, 3)
        if x > (TFTWIDTH-10):
            x = 10
            y = asm_get_charpos(font['height'], scale, y)

def lcd_draw_pixel(x, y, color, pixels=4):
    if pixels not in [1, 4]:
        raise ValueError("Pixels count must be 1 or 4")

    lcd_set_window(x, x+1, y, y+1)
    lcd_write_data(get_Npix_monoword(color, pixels=pixels))

def lcd_draw_Vline(x, y, length, color, width=1):
    if length > TFTHEIGHT: length = TFTHEIGHT
    if width > 10: width = 10
    lcd_set_window(x, x+(width-1), y, length)
    pixels = width * length
    pixels = pixels//4 if pixels >= 4 else pixels
    word = get_Npix_monoword(color) * pixels
    lcd_write_data(word)

def lcd_draw_Hline(x, y, length, color, width=1):
    if length > TFTWIDTH: length = TFTWIDTH
    if width > 10: width = 10
    lcd_set_window(x, length, y, y+(width-1))
    pixels = width * length
    pixels = pixels//4 if pixels >= 4 else pixels
    word = get_Npix_monoword(color) * pixels
    lcd_write_data(word)

def lcd_draw_rect(x, y, width, height, color, border=1, fillcolor=None):
    if width > TFTWIDTH: width = TFTWIDTH
    if height > TFTHEIGHT: height = TFTHEIGHT
    if border:
        if border > width//2:
            border = width//2-1
        X, Y = x, y
        for i in range(2):
            Y = y+height-(border-1) if i == 1 else y
            lcd_draw_Hline(X, Y, x+width, color, border)

            Y = y+(border-1) if i == 1 else y
            X = x+width-(border-1) if i == 1 else x
            lcd_draw_Vline(X, Y, y+height, color, border)
    else:
        fillcolor = color

    if fillcolor:
        xsum = x+border
        ysum = y+border
        dborder = border*2
        lcd_set_window(xsum, xsum+width-dborder, ysum, ysum+height-dborder)
        pixels = (width-dborder)*8+border+width
        rows   = (height)

        word = get_Npix_monoword(fillcolor) * (pixels//4)

        if rows < 1:
            lcd_write_data(word)
        else:
            i=0
            while i < (rows//4):
                lcd_write_data(word)
                i+=1

def lcd_fill_monocolor(color, margin=0):
    lcd_draw_rect(margin, margin, TFTWIDTH, TFTHEIGHT, color, border=0)

def set_word_length(word):
    return bin(word)[3:]

def lcd_fill_bicolor(data, x, y, width, height, color, bgcolor=WHITE, scale=1):
    lcd_set_window(x, x+(height*scale)-1, y, y+(width*scale)-1)
    bgpixel = get_Npix_monoword(bgcolor, pixels=1) * scale
    pixel = get_Npix_monoword(color, pixels=1) * scale
    words = ''.join(map(set_word_length, data))
    words = bytes(words, 'ascii').replace(b'0', bgpixel).replace(b'1', pixel)
    lcd_write_data(words)

def get_x_perimeter_point(x, degrees, radius):
    sin = math.sin(math.radians(degrees))
    x = int(x+(radius*sin))
    return x

def get_y_perimeter_point(y, degrees, radius):
    cos = math.cos(math.radians(degrees))
    y = int(y-(radius*cos))
    return y

def lcd_draw_circle_filled(x, y, radius, color):
    tempY = 0
    for i in range(180):
        xNeg = get_x_perimeter_point(x, 360-i, radius-1)
        xPos = get_x_perimeter_point(x, i, radius)
        if i > 89:
            Y = get_y_perimeter_point(y, i, radius-1)
        else:
            Y = get_y_perimeter_point(y, i, radius)
        if i == 90: xPos = xPos-1
        if tempY != Y and tempY > 0:
            length = xPos+1
            lcd_draw_Hline(xNeg, Y, length, color, width=2)
        tempY = Y

def lcd_draw_circle(x, y, radius, color, border=1, degrees=360):
    width = height = border
    for i in range(degrees):
        X = get_x_perimeter_point(x, i, radius-border)
        Y = get_y_perimeter_point(y, i, radius-border)
        if i == 90: X = X-1
        elif i == 180: Y = Y-1
        if border < 4:
            lcd_draw_pixel(X, Y, color, pixels=1)
        else:
            lcd_draw_rect(X, Y, width, height, color, border=0)

def lcd_draw_oval_filled(x, y, xradius, yradius, color):
    tempY = 0
    for i in range(180):
        xNeg = get_x_perimeter_point(x, 360-i, xradius)
        xPos = get_x_perimeter_point(x, i, xradius)
        Y    = get_y_perimeter_point(y, i, yradius)

        if i > 89: Y = Y-1
        if tempY != Y and tempY > 0:
            length = xPos+1
            lcd_draw_Hline(xNeg, Y, length, color, width=2)
        tempY = Y
        
# TODO:
# 1. Check chars positioning, change in lcd_set_window position
# 2. optimize:
def lcd_print_char(char, x, y, color, font, bgcolor=BLACK, cont=False, scale=1):
    scale = 8 if scale > 8 else scale
    index = 'ch' + str(ord(char))
    chrwidth = len(font[index])
    height = font['height']
    data   = font[index]
    X = TFTHEIGHT-y-height
    Y = x
    set_char_orientation()
    lcd_fill_bicolor(data, X, Y, chrwidth, height, color, bgcolor, scale=scale)
    if not cont:
        set_graph_orientation()

# TODO:
# 1. Split by words and high string must be rendered in multiply lines
# 2. optimize:
def lcd_print_ln(string, x, y, color, font=Arial_14, bgcolor=WHITE, scale=1):
    scale = 4 if scale > 4 else scale
    for i in range(len(string)):
        chrwidth = len(font['ch' + str(ord(string[i]))])
        cont = False if i == len(string)-1 else True
        lcd_print_char(string[i], x, y, color, font, bgcolor=bgcolor, cont=cont, scale=scale)
        x += asm_get_charpos(chrwidth, scale-(scale//2), 3)
        if x > (TFTWIDTH-10):
            x = 10
            y -= font['height'] * scale-(scale//2)

# solution from forum.micropython.org
# Need to be understandet
@micropython.asm_thumb
def reverse(r0, r1):               # bytearray, len(bytearray)

    b(loopend)

    label(loopstart)
    ldrb(r2, [r0, 0])
    ldrb(r3, [r0, 1])
    strb(r3, [r0, 0])
    strb(r2, [r0, 1])
    add(r0, 2)

    label(loopend)
    sub (r1, 2)  # End of loop?
    bpl(loopstart)

# TODO:
# 1. read image data (width, height, size, startbit) from BMP header regs
# and set them to rendering params
def render_bmp(filename, x, y, width, height, cached=True):
    path = 'images/'
    startbit = 138
    memread = 480
    if filename + '.cache' not in os.listdir(path + '/cache'):
        cached = False
    if cached:
        path = 'images/cache/'
        filename = filename + '.cache'
        startbit = 9
        memread = 512
    set_image_orientation()
    lcd_set_window(x, (width)+x, y, (height)+y)
    with open(path + filename, 'rb') as f:
        f.seek(startbit)
        while True:
            try:
                if cached:
                    lcd_write_data(f.read(memread))
                else:
                    data = bytearray(f.read(480))
                    reverse(data, len(data))
                    lcd_write_data(data)
            except OSError: break
    set_graph_orientation()

def clear_cache(path):
    for obj in os.listdir(path):
        if obj.endswith('.cache'):
            os.remove(path + '/' + obj)

def cache_image(image, width, height):
    memread = 480
    startbit = 138
    path = 'images/cache/'
    c = open(path + image + '.cache', 'ab')
    c.write(array.array('H', (memread,)))   #
    c.write(b'\n')                          #
    c.write(bytearray([height]))            #   Before image header realization
    c.write(b"\n")                          #   test feature
    c.write(bytearray([width]))             #
    c.write(b'\n')                          #
    data = '1'
    with open('images/' + image, 'rb') as f:
        f.seek(startbit)
        while len(data) != 0:
            try:
                data = bytearray(f.read(memread))
                reverse(data, len(data))
                c.write(data)
            except OSError: break
    c.close()
    print('Cached:', image)

# TEST CODE
if __name__ == "__main__":
    lcd_init()

    starttime = pyb.micros()//1000
    # some code
    print('executed in:', (pyb.micros()//1000-starttime)/1000, 'seconds')
