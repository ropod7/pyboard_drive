#
# The MIT License (MIT)
# Copyright (c) 2016. Roman Podgaiski
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# ATTENTION:
#
#    You will have PyBoard firmware >v1.7. This version give us more
#    opportunities with reading from SD card. Earlier versions are useless
#    in this driver scope.
#
# DESCRIPTION:
#
# lcd.py - contains ILI TFT LCD controllers driving classes
# Data transfer using 4-line Serial protocol (Series II)
# 16-bit RGB Color (R:5-bit; G:6-bit; B:5-bit)
# About 30Hz monocolor screen refresh
#
# Default is portrait mode:
# lcd = LCD( [ portrait = True ] )
#    width  is 240px
#    height is 320px
#
# Set up landscape mode:
# lcd = LCD( portrait = False )
#    width  is 320px
#    height is 240px
#
# Template method for orientation management by Accel:
#    Changing mode on the air by calling:
#    lcd.setPortrait( True [or False] )
#    OR:
#    lcd.portrait = True [or False]
#
# User don't need to import fonts, they imports by python code
# Avaliable fonts:
#    'VeraMono_10',
#    'Vera_10',
#    'Arial_14',
#    'Vera_14',
#    'VeraMono_14',
#    'Pitch_14',
#    'Pitch_22',
#    'Vera_23',
#    'VeraMono_23',
#    'Heydings_23',
#    'Entypo_14',
#    'Entypo_23',
#
#    define fonts by typing in string format:
#        string = lcd.initCh(color=(R,G,B), font='Arial_14', [scale=1])
#    You may change string objects font by:
#        string.font = 'Arial_14'
#    printing line:
#        string.printLn('Hello, World', x, y, [scale=1])

import os
import struct
import math
import array
import gc

import pyb, micropython
from pyb import SPI, Pin

#from decorators import dimensions
from registers import regs
from colors import *

micropython.alloc_emergency_exception_buf(100)

imgcachedir = 'images/cache'
if 'cache' not in os.listdir('images'):
    try:
        os.mkdir(imgcachedir)
    except OSError: pass

rate = 42000000

class ILI:
    _cnt  = 0
    _regs = dict()
    _spi  = object()
    _rst  = object()
    _csx  = object()
    _dcx  = object()
    _portrait  = True

    _tftwidth  = 240   # TFT width Constant
    _tftheight = 320   # TFT height Constant

    _curwidth  = 240   # Current TFT width
    _curheight = 320   # Current TFT height

    def __init__(self, rstPin='X3', csxPin='X4', dcxPin='X5', port=1, rate=rate,
                chip='ILI9341', portrait=True):
        if ILI._cnt == 0:
            ILI._regs = regs[chip]
            ILI._spi  = SPI(port, SPI.MASTER, baudrate=rate, polarity=1, phase=1)
            ILI._rst  = Pin(rstPin, Pin.OUT_PP)    # Reset Pin
            ILI._csx  = Pin(csxPin, Pin.OUT_PP)    # CSX Pin
            ILI._dcx  = Pin(dcxPin, Pin.OUT_PP)    # D/Cx Pin
            self.reset()
            self._initILI()

        self.setPortrait(portrait)
        ILI._cnt += 1
        self._gcCollect()

    def reset(self):
        ILI._rst.low()                #
        pyb.delay(1)                  #    RESET LCD SCREEN
        ILI._rst.high()               #

    def setPortrait(self, portrait):
        self.portrait = portrait

    def _gcCollect(self):
        gc.collect()

    def _setWH(self):
        if ILI._portrait:
            ILI._curheight = self.TFTHEIGHT = ILI._tftheight
            ILI._curwidth  = self.TFTWIDTH  = ILI._tftwidth
        else:
            ILI._curheight = self.TFTHEIGHT = ILI._tftwidth
            ILI._curwidth  = self.TFTWIDTH  = ILI._tftheight
        self._graph_orientation()

    def _initILI(self):
        self._write_cmd(ILI._regs['LCDOFF'])   # Display OFF
        pyb.delay(10)
        self._write_cmd(ILI._regs['SWRESET'])  # Reset SW
        pyb.delay(50)
        self._graph_orientation()
        self._write_cmd(ILI._regs['PTLON'])    # Partial mode ON
        self._write_cmd(ILI._regs['PIXFMT'])   # Pixel format set
        #self._write_data(0x66)    # 18-bit/pixel
        self._write_data(0x55)    # 16-bit/pixel
        self._write_cmd(ILI._regs['GAMMASET'])
        self._write_data(0x01)
        self._write_cmd(ILI._regs['ETMOD'])    # Entry mode set
        self._write_data(0x07)
        self._write_cmd(ILI._regs['SLPOUT'])   # sleep mode OFF
        pyb.delay(10)
        self._write_cmd(ILI._regs['LCDON'])
        pyb.delay(10)
        self._write_cmd(ILI._regs['RAMWR'])

    def _write(self, word, dc, recv):
        dcs = ['cmd', 'data']

        DCX = dcs.index(dc) if dc in dcs else None
        ILI._csx.low()
        ILI._dcx.value(DCX)
        if recv:
            fmt = '>BI'
            recv = bytearray(5)
            data = ILI._spi.send_recv(struct.pack(fmt, word), recv=recv)
            ILI._csx.high()
            return data

        ILI._spi.send(word)
        ILI._csx.high()

    # for now decoded just recv color (or data readed from memory)
    def _decode_recv_data(self, data):
        # For example:
        #    1. recieving sets 5 bytes
        #    2. firs 2 of them are useless (or null bytes)
        #    3. and just 3 last of them having a useful data:
        #        - those 3 bytes are RGB bytes (if we are reading from memory)
        #        - those 3 bytes have a 7 useful bits (and doesn't matter which color is)
        #        - we must get from them:
        #            * just 5 largest bits for R and B colors
        #            * just 6 largest bits for G color
        # next 2 lines sorting useful data
        # getting 4 last bytes
        data = struct.unpack('<BI', data)[1]
        # reversing them
        data = struct.pack('>I', data)
        # getting just 3 bytes from bytearray as BGR
        data = struct.unpack('>3B', data)
        # with those 3 assignmentations we sorting useful bits for each color
        red   = (((data[2]>>2) & 31) << 11)
        green = (((data[1]>>1) & 63) << 5)
        blue  = ((data[0]>>2) & 31)
        # setting them to 16 bit color
        data = red | green | blue
        data = struct.pack('>H', data)
        return data

    def _write_cmd(self, word, recv=None):
        data = self._write(word, 'cmd', recv)
        return data

    def _write_data(self, word):
        self._write(word, 'data', recv=None)

    def _write_words(self, words):
        wordL = len(words)
        wordL = wordL if wordL > 1 else ""
        fmt = '>{0}B'.format(wordL)
        words = struct.pack(fmt, *words)
        self._write_data(words)

    def _graph_orientation(self):
        self._write_cmd(ILI._regs['MADCTL'])   # Memory Access Control
        # Portrait:
        # | MY=0 | MX=1 | MV=0 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
        # OR Landscape:
        # | MY=0 | MX=0 | MV=1 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
        data = 0x48 if ILI._portrait else 0x28
        self._write_data(data)

    def _char_orientation(self):
        self._write_cmd(ILI._regs['MADCTL'])   # Memory Access Control
        # Portrait:
        # | MY=1 | MX=1 | MV=1 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
        # OR Landscape:
        # | MY=0 | MX=1 | MV=1 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
        data = 0xE8 if ILI._portrait else 0x58
        self._write_data(data)

    def _image_orientation(self):
        self._write_cmd(ILI._regs['MADCTL'])   # Memory Access Control
        # Portrait:
        # | MY=0 | MX=1 | MV=0 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
        # OR Landscape:
        # | MY=0 | MX=1 | MV=0 | ML=1 | BGR=1 | MH=0 | 0 | 0 |
        data = 0xC8 if ILI._portrait else 0x68
        self._write_data(data)

    def _set_window(self, x0, y0, x1, y1):
        # Column Address Set
        self._write_cmd(ILI._regs['CASET'])
        self._write_words(((x0>>8) & 0xFF, x0 & 0xFF, (y0>>8) & 0xFF, y0 & 0xFF))
        # Page Address Set
        self._write_cmd(ILI._regs['PASET'])
        self._write_words(((x1>>8) & 0xFF, x1 & 0xFF, (y1>>8) & 0xFF, y1 & 0xFF))
        # Memory Write
        self._write_cmd(ILI._regs['RAMWR'])

    def _get_Npix_monoword(self, color):
        if color == WHITE:
            word = 0xFFFF
        elif color == BLACK:
            word = 0
        else:
            R, G, B = color
            word = (R<<11) | (G<<5) | B
        word = struct.pack('>H', word)
        return word

    # Method writed by MCHobby https://github.com/mchobby
    # Transform a RGB888 color to RGB565 color tuple.
    def rgbTo565(self, r, g, b):
        return (r>>3, g>>2, b>>3)

    @property
    def portrait(self):
        return ILI._portrait

    @portrait.setter
    def portrait(self, portr):
        if isinstance(portr, bool):
            ILI._portrait = portr
        else:
            raise ValueError('portrait setting must be a boolean')
        self._setWH()

class BaseDraw(ILI):
    def __init__(self, **kwargs):
        super(BaseDraw, self).__init__(**kwargs)

    def _set_ortho_line(self, width, length, color):
        pixels = width * length
        word = self._get_Npix_monoword(color) * pixels
        self._write_data(word)

    def drawPixel(self, x, y, color, pixels=4):
        if pixels not in [1, 4]:
            raise ValueError("Pixels count must be 1 or 4")

        self._set_window(x, x+1, y, y+1)
        self._write_data(self._get_Npix_monoword(color) * pixels)

    def drawVline(self, x, y, length, color, width=1):
        if length > self.TFTHEIGHT: length = self.TFTHEIGHT
        if width > 10: width = 10
        self._set_window(x, x+(width-1), y, y+length)
        self._set_ortho_line(width, length, color)

    def drawHline(self, x, y, length, color, width=1):
        if length > self.TFTWIDTH: length = self.TFTWIDTH
        if width > 10: width = 10
        self._set_window(x, x+length, y, y+(width-1))
        self._set_ortho_line(width, length, color)

    # Method writed by MCHobby https://github.com/mchobby
    # TODO:
    # 1. support border > 1
    def drawLine(self, x, y, x1, y1, color):
        if x==x1:
            self.drawVline( x, y if y<=y1 else y1, abs(y1-y), color )
        elif y==y1:
            self.drawHline( x if x<=x1 else x1, y, abs(x-x1), color )
        else:
            # keep positive range for x
            if x1 < x:
              x,x1 = x1,x
              y,y1 = y1,y
            r = (y1-y)/(x1-x)
            # select ratio > 1 for fast drawing (and thin line)
            if abs(r) >= 1:
                for i in range( x1-x+1 ):
                    if (i==0): # first always a point
                        self.drawPixel( x+i, math.trunc(y+(r*i)), color )
                    else:
                        # r may be negative when drawing to wrong way > Fix it when drawing
                        self.drawVline( x+i, math.trunc(y+(r*i)-r)+(0 if r>0 else math.trunc(r)), abs(math.trunc(r)), color )
            else:
                # keep positive range for y
                if y1 < y:
                    x,x1 = x1,x
                    y,y1 = y1,y
                # invert the ratio (should be close of r = 1/r)
                r = (x1-x)/(y1-y)
                for i in range( y1-y+1 ):
                    if( i== 0): # starting point is always a point
                        self.drawPixel( math.trunc(x+(r*i)), y+i, color )
                    else:
                        # r may be negative when drawing the wrong way > fix it to draw positive
                        self.drawHline( math.trunc(x+(r*i)-r)+(0 if r>0 else math.trunc(r)), y+i, abs(math.trunc(r)), color )

    def drawRect(self, x, y, width, height, color, border=1, fillcolor=None):
        border = 10 if border > 10 else border
        if width > self.TFTWIDTH: width = self.TFTWIDTH
        if height > self.TFTHEIGHT: height = self.TFTHEIGHT
        height = 2 if height < 2 else height
        width  = 2 if width  < 2 else width
        self._graph_orientation()
        if border:
            if border > width//2:
                border = width//2-1
            X, Y = x, y
            for i in range(2):
                Y = y+height-(border-1) if i == 1 else y
                self.drawHline(X, Y, width, color, border)

                if border > 1:
                    Y = y+1
                    H = height
                else:
                    Y = y
                    H = height + 1
                X = x+width-(border-1) if i == 1 else x
                self.drawVline(X, Y, H, color, border)
        else:
            fillcolor = color

        if fillcolor:
            xsum = x+border
            ysum = y+border
            dborder = border*2
            self._set_window(xsum, xsum+width-dborder, ysum, ysum+height-dborder)
            # if MemoryError, try to set higher porsion value
            portion = 16
            pixels = width * (height//portion) if height >= 30 else width * height
            word = self._get_Npix_monoword(fillcolor) * pixels
            self._gcCollect()
            i=0
            times = 20 if height < 80 else portion + 1
            while i < (times):
                self._write_data(word)
                i+=1

    def fillMonocolor(self, color, margin=0):
        margin = 80 if margin > 80 else margin
        width = self.TFTWIDTH-margin*2
        height = self.TFTHEIGHT-margin*2
        self.drawRect(margin, margin, width, height, color, border=0)

    def _get_x_perimeter_point(self, x, degrees, radius):
        sin = math.sin(math.radians(degrees))
        x = int(x+(radius*sin))
        return x

    def _get_y_perimeter_point(self, y, degrees, radius):
        cos = math.cos(math.radians(degrees))
        y = int(y-(radius*cos))
        return y

    def drawCircleFilled(self, x, y, radius, color):
        tempY = 0
        for i in range(180):
            xNeg = self._get_x_perimeter_point(x, 360-i, radius-1)
            xPos = self._get_x_perimeter_point(x, i, radius)
            if i > 89:
                Y = self._get_y_perimeter_point(y, i, radius-1)
            else:
                Y = self._get_y_perimeter_point(y, i, radius+1)
            if i == 90: xPos = xPos-1
            if tempY != Y and tempY > 0:
                length = xPos+1
                self.drawHline(xNeg, Y, length-xNeg, color, width=4)
            tempY = Y

    def drawCircle(self, x, y, radius, color, border=1, degrees=360, startangle=0):
        border = 5 if border > 5 else border
        # adding startangle to degrees
        if startangle > 0:
            degrees += startangle
        if border > 1:
            x = x - border//2
            y = y - border//2
            radius = radius-border//2
        for i in range(startangle, degrees):
            X = self._get_x_perimeter_point(x, i, radius)
            Y = self._get_y_perimeter_point(y, i, radius)
            if   i == 90:  X = X-1
            elif i == 180: Y = Y-1
            self.drawRect(X, Y, border, border, color, border=0)

    def drawOvalFilled(self, x, y, xradius, yradius, color):
        tempY = 0
        for i in range(180):
            xNeg = self._get_x_perimeter_point(x, 360-i, xradius)
            xPos = self._get_x_perimeter_point(x, i, xradius)
            Y    = self._get_y_perimeter_point(y, i, yradius)

            if i > 89: Y = Y-1
            if tempY != Y and tempY > 0:
                length = xPos+1
                self.drawHline(xNeg, Y, length-xNeg, color, width=4)
            tempY = Y

class BaseChars(ILI, BaseDraw):
    def __init__(self, color=BLACK, font=None, bgcolor=None, scale=1, **kwargs):
        super(BaseChars, self).__init__(**kwargs)
        self._fontColor = color
        if font is not None:
            import fonts
            self._gcCollect()
            font = fonts.importing(font)
            self._font = font
            del(fonts)
        else:
            raise ValueError("font not defined")
        self._portrait = ILI._portrait
        self._bgcolor = bgcolor if bgcolor is None else self._get_Npix_monoword(bgcolor)
        self._fontscale = scale

    def initCh(self, **kwargs):
        ch = BaseChars(portrait=ILI._portrait, **kwargs)
        return ch

    def _setWH(self):
        if ILI._portrait:
            self.TFTHEIGHT = ILI._tftheight
            self.TFTWIDTH  = ILI._tftwidth
        else:
            self.TFTHEIGHT = ILI._tftwidth
            self.TFTWIDTH  = ILI._tftheight
        self._char_orientation()

    def _check_portrait(self):
        if self.portrait != ILI._portrait:
            self.portrait = ILI._portrait

    @staticmethod
    @micropython.asm_thumb
    def _asm_get_charpos(r0, r1, r2):
        mul(r0, r1)
        adc(r0, r2)

    def _get_bgcolor(self, x, y):
        self._set_window(x, x, y, y)
        data = self._write_cmd(self._regs['RAMRD'], recv=True)
        data = self._decode_recv_data(data)
        return data

    def _set_word_length(self, data):
        return bin(data)[3:] * self._fontscale

    def _fill_bicolor(self, data, x, y, width, height, scale=None):
        bgcolor = self._get_bgcolor(x, y) if not self._bgcolor else self._bgcolor
        color = self._fontColor
        self._set_window(x, x+(height*scale)-1, y, y+(width*scale))
        bgpixel = bgcolor * scale
        pixel = self._get_Npix_monoword(color) * scale
        words = ''.join(map(self._set_word_length, data))
        # Garbage collection
        self._gcCollect()
        words = bytes(words, 'ascii').replace(b'0', bgpixel).replace(b'1', pixel)
        self._write_data(words)
        self._graph_orientation()

    def printChar(self, char, x, y, scale=None):
        if scale is None:
            scale = self._fontscale
        font = self._font
        self._check_portrait()
        self._fontscale = scale = 5 if scale > 5 else scale
        index = ord(char)
        height = font['height']
        try:
            chrwidth = len(font[index]) * scale
            data = font[index]
        except KeyError:
            data = None
            chrwidth = font['width'] * scale
        X = self.TFTHEIGHT - y - (height * scale) + scale
        Y = x
        self._char_orientation()
        # Garbage collection
        self._gcCollect()
        if data is None:
            self._graph_orientation()
            self.drawRect(x, y, height, chrwidth, self._fontColor, border=2*scale)
        else:
            self._fill_bicolor(data, X, Y, chrwidth, height, scale=scale)

    # TODO:
    # add split by new line
    def printLn(self, string, x, y, bc=False, scale=None):
        if scale is None:
            scale = self._fontscale
        self._check_portrait()
        font = self._font
        X, Y = x, y
        scale = 3 if scale > 3 else scale
        for word in string.split(' '):
            lnword = len(word)
            outofscreen = x + lnword * (font['width']-font['width']//3) * scale
            if (outofscreen) >= (self.TFTWIDTH-10):
                x = X
                y += (font['height'] + 2) * scale
            for i in range(lnword):
                chrwidth = len(font[ord(word[i])])
                self.printChar(word[i], x, y, scale=scale)
                if chrwidth == 1:
                    chpos = scale + 1 if scale > 2 else scale - 1
                else:
                    chpos = scale
                x += self._asm_get_charpos(chrwidth, chpos, 3)
            x += self._asm_get_charpos(len(font[32]), chpos, 3)

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, font):
        import fonts
        font = fonts.importing(font)
        self._font = font
        del(fonts)

    @property
    def fontscale(self):
        return self._fontscale

    @property
    def portrait(self):
        return self._portrait

    @portrait.setter
    def portrait(self, portr):
        if isinstance(portr, bool):
            self._portrait = portr
        else:
            raise ValueError('set portrait as boolean')
        self._setWH()

    @property
    def resolution(self):
        print('width:  {0}px\nheight: {1}px'.format(self.TFTWIDTH, self.TFTHEIGHT))

class BaseImages(ILI):

    def __init__(self, **kwargs):
        super(BaseImages, self).__init__(**kwargs)

    # solution from forum.micropython.org
    @staticmethod
    @micropython.asm_thumb
    def _reverse(r0, r1):               # bytearray, len(bytearray)
        b(loopend)
        label(loopstart)
        ldrb(r2, [r0, 0])
        ldrb(r3, [r0, 1])
        strb(r3, [r0, 0])
        strb(r2, [r0, 1])
        add(r0, 2)
        label(loopend)
        sub(r1, 2)  # End of loop?
        bpl(loopstart)

    def _set_image_headers(self, f):
        headers = list()
        if f.read(2) != b'BM':
            raise OSError('Not a valid BMP image')
        for pos in (10, 18, 22):                                 # startbit, width, height
            f.seek(pos)
            headers.append(struct.unpack('<H', f.read(2))[0])    # read double byte
        return headers

    def _get_image_points(self, pos, width, height):
        if isinstance(pos, (list, tuple)):
            x, y = pos
        else:
            x = 0 if width  == self.TFTWIDTH else (self.TFTWIDTH-width)//2
            y = 0 if height == self.TFTHEIGHT else (self.TFTHEIGHT-height)//2
        return x, y

    # Using in renderBmp method
    def _render_bmp_image(self, filename, pos):
        path = 'images/'
        memread = 512
        with open(path + filename, 'rb') as f:
            startbit, width, height = self._set_image_headers(f)
            if width < self.TFTWIDTH:
                width -= 1
            x, y = self._get_image_points(pos, width, height)
            self._set_window(x, (width)+x, y, (height)+y)
            f.seek(startbit)
            while True:
                try:
                    data = bytearray(f.read(memread))
                    self._reverse(data, len(data))
                    self._write_data(data)
                except OSError as err:
                    print(err)
                    break

    # Using in renderBmp method
    def _render_bmp_cache(self, filename, pos):
        filename = filename + '.cache'
        startbit = 8
        memread = 1024 * 10
        self._gcCollect()
        with open(imgcachedir + '/' + filename, 'rb') as f:
            width = struct.unpack('H', f.readline())[0]
            height = struct.unpack('H', f.readline())[0]
            print(filename, 'sizes:', str(width) + 'x' + str(height))
            if width < self.TFTWIDTH:
                width -= 1
            x, y = self._get_image_points(pos, width, height)
            self._set_window(x, (width)+x, y, (height)+y)
            f.seek(startbit)
            while True:
                try:
                    self._write_data(f.read(memread))
                except OSError as err:
                    print(err)
                    break
        self._gcCollect()

    # TODO:
    # 1. resize large images to screen resolution
    # 2. if part of image goes out of the screen, must to be rendered
    # only displayed part
    def renderBmp(self, filename, pos=None, cached=True, bgcolor=None):
        self._image_orientation()
        self._gcCollect()
        notcached = ''
        if bgcolor:
            self.fillMonocolor(bgcolor)
        if filename + '.cache' not in os.listdir('images/cache'):
            notcached = 'not cached'
        if cached:
            self._render_bmp_cache(filename, pos)
        elif not cached or notcached:
            print(filename, 'image', notcached)
            self._render_bmp_image(filename, pos)
        self._graph_orientation()

    def clearImageCache(self, path):
        for obj in os.listdir(path):
            if obj.endswith('.cache'):
                os.remove(path + '/' + obj)

    # TODO:
    # 1. resize large images to screen resolution
    def cacheImage(self, image, imgdir='images'):
        self.fillMonocolor(BLACK)
        strings = self.initCh(color=DARKGREY, font='Arial_14')
        strings.printLn("Caching:", 25, 25)
        strings.printLn(image + '...', 45, 45)
        memread = 60                                      # less memory write - more stable result
        cachepath = imgdir + '/cache'
        cachedimage = image + '.cache'
        if cachedimage in os.listdir(cachepath):
            os.remove(cachepath + '/' + cachedimage)
        with open(imgdir + '/' + image, 'rb') as f:
            startbit, width, height = self._set_image_headers(f)

            c = open(cachepath + '/' + cachedimage, 'wb')
            for val in [width, height]:
                c.write(bytes(array.array('H', [val])) + b"\n")

            f.seek(startbit)
            data = '1'
            while len(data) != 0:
                try:
                    data = bytearray(f.read(memread))
                    self._reverse(data, len(data))
                    c.write(data)
                except OSError as err:
                    print('OSError:', err)
                    break
            c.close()
        self.fillMonocolor(BLACK)
        strings.printLn(image + " cached", 25, 25)
        print('Cached:', image)
        del(strings)
        self._gcCollect()

    def cacheAllImages(self, imgdir='images'):
        if 'cache' not in os.listdir(imgdir):
            os.chdir(imgdir)
            os.mkdir('cache')
            try:
                os.chdir('/sd')
            except OSError:
                os.chdir('/flash')
        for image in os.listdir(imgdir):
            if image == 'cache': continue
            self.cacheImage(image, imgdir=imgdir)
            pyb.delay(100)            # delay for better and stable result

class BaseTests(BaseDraw, BaseChars, BaseImages):

    def __init__(self, **kwargs):
        super(BaseTests, self).__init__(**kwargs)

    def charsTest(self, color, font=None, bgcolor=None, scale=1):
        ch = self.initCh(color=color, font=font, bgcolor=bgcolor, scale=scale)
        scale = 3 if scale > 2 else 1
        x = y = 5
        font = ch._font
        fwidth = font['width']
        for i in range(33, 256):
            try:
                chrwidth = len(font[i])
            except KeyError:
                continue
            ch.printChar(chr(i), x, y, scale=scale)
            x += self._asm_get_charpos(chrwidth, scale, 3)
            if x > (self.TFTWIDTH-fwidth*scale):
                x = 10
                y = self._asm_get_charpos(font['height'], scale, y)

    def renderImageTest(self, cached=True, path='images', cpath='cache',
                    delay=0, bgcolor=BLACK): # images/cache path
        starttime = pyb.micros()//1000
        cachelist = os.listdir('images/cache')
        print('cached images:', cachelist)
        for image in os.listdir(path):
            if image != cpath and image.endswith('bmp'):
                self.renderBmp(image, cached=cached, bgcolor=bgcolor)
                if delay:
                    pyb.delay(delay)
        return (pyb.micros()//1000-starttime)/1000

    def charsBGcolorTest(self, color=BLACK, font=None, scale=3):
        if font is None:
            raise ValueError('font is not defined')
        s = self.initCh(font=font, color=color, scale=scale)
        x = self.TFTWIDTH//2 - (s.font['width']//2) * scale
        y = self.TFTHEIGHT//2 - (s.font['height']//2) * scale
        colors = [BLACK, NAVY, DARKGREEN, DARKCYAN, MAROON, PURPLE, OLIVE,
                LIGHTGREY, DARKGREY, BLUE, GREEN, CYAN, RED, MAGENTA, YELLOW,
                WHITE, ORANGE, GREENYELLOW]
        j = 33
        self._gcCollect()
        for i in range((255-33)//16):
            for clr in colors:
                if isinstance(color, tuple) and color != clr:
                    self.fillMonocolor(clr)
                    s.printChar(chr(j), x, y)
                    j += 1
                    pyb.delay(100)
        self._gcCollect()

    # test shows as smooth screen refreshes
    def rgbInfillTest(self):
        red = green = blue = 0
        for i in range(65536):
            if red > 31:
                red = 0
            if green > 63:
                green = 0
            self.fillMonocolor((red, green, blue))
            red += 1
            if red == 32:
                green += 1
            if green == 64:
                blue += 1
                print(i, 'blue is', blue)


class BaseWidgets(BaseTests):

    def __init__(self, **kwargs):
        super(BaseWidgets, self).__init__(**kwargs)

    def _get_strwidth(self, char):
        return len(self.font[ord(char)])

    # WORK IN PROGRESS
    # Need test
    def widget(self, x, y, width, height, color, fillcolor, string, strobj=None,
            border=1):
        if strobj is None:
            raise ValueError('string object is None')
        self._font = strobj.font
        strscale = strobj.fontscale
        strlen = len(string)
        spaces = len(string.split(" ")) - 1
        # getting width of string
        strwidth = ((sum(map(self._get_strwidth, string)) + strlen*3) + spaces*2*3) * strscale
        strheight = strobj.font['height'] * strscale
        if strwidth > (width-5):
            width = strwidth + 20 + border * 2
        if strheight > height-5:
            height = strheight + 10
            print(height)

        self.drawRect(x, y, width, height, color, border=border, fillcolor=fillcolor)
        # setting up string x and y point
        strX = ((width - strwidth)>>1) + x
        #self.drawVline(strX+strwidth, y, 20, BLACK)
        strY = (height-((strobj.font['height']-4) * strscale))//2 + y
        strobj.printLn(string, strX, strY)
        x1, y1 = x+width, y+height
        return x, y, x1, y1

class LCD(BaseWidgets):

    def __init__(self, **kwargs):
        super(LCD, self).__init__(**kwargs)

    def reset(self):
        super(LCD, self).reset()

    def setPortrait(self, *args):
        super(LCD, self).setPortrait(*args)

    def drawPixel(self, *args, **kwargs):
        super(LCD, self).drawPixel(*args, **kwargs)

    def drawVline(self, *args, **kwargs):
        super(LCD, self).drawVline(*args, **kwargs)

    def drawHline(self, *args, **kwargs):
        super(LCD, self).drawHline(*args, **kwargs)

    def drawLine(self, *args, **kwargs):
        super(LCD, self).drawLine(*args, **kwargs)

    def drawRect(self, *args, **kwargs):
        super(LCD, self).drawRect(*args, **kwargs)

    def fillMonocolor(self, *args, **kwargs):
        super(LCD, self).fillMonocolor(*args, **kwargs)

    def drawCircleFilled(self, *args, **kwargs):
        super(LCD, self).drawCircleFilled(*args, **kwargs)

    def drawCircle(self, *args, **kwargs):
        super(LCD, self).drawCircle(*args, **kwargs)

    def drawOvalFilled(self, *args, **kwargs):
        super(LCD, self).drawOvalFilled(*args, **kwargs)

    def initCh(self, **kwargs):
        return super(LCD, self).initCh(**kwargs)

    def printChar(self, *args, **kwargs):
        super(LCD, self).printChar(*args, **kwargs)

    def printLn(self, *args, **kwargs):
        super(LCD, self).printLn(*args, **kwargs)

    def renderBmp(self, *args, **kwargs):
        super(LCD, self).renderBmp(*args, **kwargs)

    def clearImageCache(self, *args, **kwargs):
        super(LCD, self).clearImageCache(*args, **kwargs)

    def cacheImage(self, *args, **kwargs):
        super(LCD, self).cacheImage(*args, **kwargs)

    def cacheAllImages(self, *args, **kwargs):
        super(LCD, self).cacheAllImages(*args, **kwargs)

    def charsTest(self, *args, **kwargs):
        super(LCD, self).charsTest(*args, **kwargs)

    def renderImageTest(self, *args, **kwargs):
        return super(LCD, self).renderImageTest(*args, **kwargs)

    def widget(self, *args, **kwargs):
        return super(LCD, self).widget(*args, **kwargs)

if __name__ == '__main__':

    starttime = pyb.micros()//1000

    d = LCD() # or d = LCD(portrait=False) for landscape
    d.fillMonocolor(GREEN)
    d.drawRect(5, 5, 230, 310, BLUE, border=10, fillcolor=ORANGE)
    d.drawOvalFilled(120, 160, 60, 120, BLUE)
    d.drawCircleFilled(120, 160, 55, RED)
    d.drawCircle(120, 160, 59, GREEN, border=5)

    c = d.initCh(color=BLACK, bgcolor=ORANGE, font='Arial_14') # define string obj
    c.printChar('@', 30, 30)
    c.printLn('Hello BaseChar class', 30, 290)

    d.setPortrait(False)    # Changing mode to landscape

    d.renderBmp("test.bmp", (0, 0))

    # last time executed in: 1.379 seconds
    print('executed in:', (pyb.micros()//1000-starttime)/1000, 'seconds')