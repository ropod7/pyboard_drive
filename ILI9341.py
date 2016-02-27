#
#    WORK IN PROGRESS
#
# main.py - controlling TFT LCD ILI9341
# Data transfer using 4-line Serial protocol (Series II)
# 16-bit RGB Color (R:5-bit; G:6-bit; B:5-bit)
# About 30Hz monocolor screen refresh
#

import os
import struct
import math

import pyb, micropython
from pyb import SPI, Pin

micropython.alloc_emergency_exception_buf(100)

rate = 42000000

spi = SPI(1, SPI.MASTER, baudrate=rate, polarity=1, phase=1, bits=8)
csx = Pin('X4', Pin.OUT_PP)    # CSX Pin
dcx = Pin('X5', Pin.OUT_PP)    # D/Cx Pin
rst = Pin('X3', Pin.OUT_PP)    # Reset Pin

# Fonts definitions:
Arial_14 = dict(
    width  = 0x0D, # width
    height = 0x0E, # height

    # font data
    ch32 = [0x4000],                                           # <space> 0x20
    ch33 = [0x4BFC],                                           # 33 !
    ch34 = [0x403c, 0x4000, 0x403c],                           # 34 "
    ch35 = [0x4120, 0x4f20, 0x41f0, 0x412c, 0x4f20, 0x41f0,
            0x412c, 0x4120],                                   # 35 #
    ch36 = [0x4430, 0x4848, 0x4844, 0x5ffe, 0x4884, 0x4484,
            0x4308],                                           # 36 $
    ch37 = [0x4038, 0x4044, 0x4844, 0x4638, 0x4180, 0x4060,
            0x4718, 0x4884, 0x4880, 0x4700],                   # 37 %
    ch38 = [0x4700, 0x48b8, 0x4844, 0x48c4, 0x4924, 0x4618,
            0x4500, 0x4800],                                   # 38 &
    ch39 = [0x403c],                                           # 39 '
    ch40 = [0x4ff8, 0x580c, 0x6002],                           # 40 (
    ch41 = [0x6002, 0x580c, 0x4ff8],                           # 41 )
    ch42 = [0x4008, 0x4028, 0x401c, 0x4028, 0x4008],           # 42 *
    ch43 = [0x4080, 0x4080, 0x4080, 0x47f0, 0x4080, 0x4080,
            0x4080],                                           # 43 +
    ch44 = [0x7800],                                           # 44 ,
    ch45 = [0x4100, 0x4100, 0x4100, 0x4100],                   # 45 -
    ch46 = [0x4800],                                           # 46 .
    ch47 = [0x4c00, 0x4380, 0x4070, 0x400c],                   # 47 /
    ch48 = [0x47f8, 0x4804, 0x4804, 0x4804, 0x4804, 0x47f8],   # 48 0
    ch49 = [0x4010, 0x4008, 0x4ffc],                           # 49 1
    ch50 = [0x4818, 0x4c04, 0x4a04, 0x4904, 0x4884, 0x4878],   # 50 2
    ch51 = [0x4618, 0x4804, 0x4844, 0x4844, 0x4844, 0x47b8],   # 51 3
    ch52 = [0x4300, 0x4280, 0x4260, 0x4210, 0x4208, 0x4ffc,
            0x4200],                                           # 52 4
    ch53 = [0x4670, 0x482c, 0x4824, 0x4824, 0x4c24, 0x43c4],   # 53 5
    ch54 = [0x47f0, 0x4888, 0x4844, 0x4844, 0x4844, 0x4788],   # 54 6
    ch55 = [0x4004, 0x4004, 0x4e04, 0x41c4, 0x4034, 0x400c],   # 55 7
    ch56 = [0x47b8, 0x4844, 0x4844, 0x4844, 0x4844, 0x47b8],   # 56 8
    ch57 = [0x4478, 0x4884, 0x4884, 0x4884, 0x4444, 0x43f8],   # 57 9
    ch58 = [0x4810],                                           # 58 :
    ch59 = [0x7810],                                           # 59 ;
    ch60 = [0x4080, 0x4140, 0x4140, 0x4220, 0x4220, 0x4410],   # 60 <
    ch61 = [0x4120, 0x4120, 0x4120, 0x4120, 0x4120, 0x4120],   # 61 =
    ch62 = [0x4410, 0x4220, 0x4220, 0x4140, 0x4140, 0x4080],   # 62 >
    ch63 = [0x4018, 0x4004, 0x4b04, 0x4084, 0x4044, 0x4038],   # 63 ?
    ch64 = [0x47c0, 0x5830, 0x6008, 0x67c4, 0x6422, 0x6412,
            0x6412, 0x6212, 0x67a2, 0x6472, 0x6804, 0x6618,
            0x51e0],                                           # 64 @
    ch65 = [0x4c00, 0x4300, 0x41c0, 0x4138, 0x4104, 0x4138,
            0x41c0, 0x4300, 0x4c00],                           # 65 A
    ch66 = [0x4ffc, 0x4844, 0x4844, 0x4844, 0x4844, 0x4844,
            0x47b8],                                           # 66 B
    ch67 = [0x43f0, 0x4408, 0x4804, 0x4804, 0x4804, 0x4804,
            0x4408, 0x4210],                                   # 67 C
    ch68 = [0x4ffc, 0x4804, 0x4804, 0x4804, 0x4804, 0x4804,
            0x4408, 0x43f0],                                   # 68 D
    ch69 = [0x4ffc, 0x4844, 0x4844, 0x4844, 0x4844, 0x4844,
            0x4844],                                           # 69 E
    ch70 = [0x4ffc, 0x4044, 0x4044, 0x4044, 0x4044, 0x4044,
            0x4004],                                           # 70 F
    ch71 = [0x43f0, 0x4408, 0x4804, 0x4804, 0x4804, 0x4884,
            0x4884, 0x4488, 0x4390],                           # 71 G
    ch72 = [0x4ffc, 0x4040, 0x4040, 0x4040, 0x4040, 0x4040,
            0x4ffc],                                           # 72 H
    ch73 = [0x4ffc],                                           # 73 I
    ch74 = [0x4600, 0x4800, 0x4800, 0x4800, 0x47fc],           # 74 J
    ch75 = [0x4ffc, 0x4100, 0x4080, 0x4040, 0x40a0, 0x4310,
            0x4408, 0x4804],                                   # 75 K
    ch76 = [0x4ffc, 0x4800, 0x4800, 0x4800, 0x4800, 0x4800,
            0x4800],                                           # 76 L
    ch77 = [0x4ffc, 0x4018, 0x4060, 0x4380, 0x4c00, 0x4380,
            0x4060, 0x4018, 0x4ffc],                           # 77 M
    ch78 = [0x4ffc, 0x4008, 0x4030, 0x40c0, 0x4300, 0x4400,
            0x4ffc],                                           # 78 N
    ch79 = [0x43f0, 0x4408, 0x4804, 0x4804, 0x4804, 0x4804,
            0x4804, 0x4408, 0x43f0],                           # 79 O
    ch80 = [0x4ffc, 0x4084, 0x4084, 0x4084, 0x4084, 0x4084,
            0x4078],                                           # 80 P
    ch81 = [0x43f0, 0x4408, 0x4804, 0x4804, 0x4804, 0x4a04,
            0x4404, 0x4e08, 0x49f0],                           # 81 Q
    ch82 = [0x4ffc, 0x4084, 0x4084, 0x4084, 0x4184, 0x4284,
            0x4484, 0x4878],                                   # 82 R
    ch83 = [0x4638, 0x4844, 0x4844, 0x4844, 0x4884, 0x4884,
            0x4718],                                           # 83 S
    ch84 = [0x4004, 0x4004, 0x4004, 0x4ffc, 0x4004, 0x4004,
            0x4004],                                           # 84 T
    ch85 = [0x43fc, 0x4400, 0x4800, 0x4800, 0x4800, 0x4400,
            0x43fc],                                           # 85 U
    ch86 = [0x400c, 0x4030, 0x40c0, 0x4300, 0x4c00, 0x4300,
            0x40c0, 0x4030, 0x400c],                           # 86 V
    ch87 = [0x400c, 0x4070, 0x4380, 0x4c00, 0x4380, 0x4078,
            0x4004, 0x4078, 0x4380, 0x4c00, 0x4380, 0x4070,
            0x400c],                                           # 87 W
    ch88 = [0x4804, 0x4618, 0x4120, 0x40c0, 0x40c0, 0x4320,
            0x4618, 0x4804],                                   # 88 X
    ch89 = [0x4004, 0x4008, 0x4030, 0x4040, 0x4f80, 0x4040,
            0x4030, 0x4008, 0x4004],                           # 89 Y
    ch90 = [0x4800, 0x4c04, 0x4b04, 0x4884, 0x4844, 0x4834,
            0x480c, 0x4804],                                   # 90 Z
    ch91 = [0x7ffe, 0x6002],                                   # 91 [
    ch92 = [0x400c, 0x4070, 0x4380, 0x4c00],                   # 92 \
    ch93 = [0x6002, 0x7ffe],                                   # 93 ]
    ch94 = [0x4040, 0x4038, 0x4004, 0x4038, 0x4040],           # 94 ^
    ch95 = [0x6000, 0x6000, 0x6000, 0x6000, 0x6000, 0x6000,
            0x6000, 0x6000],                                   # 95 _
    ch96 = [0x4004, 0x4008],                                   # 96 `
    ch97 = [0x4620, 0x4910, 0x4890, 0x4890, 0x4490, 0x4fe0],   # 97 a
    ch98 = [0x4ffc, 0x4420, 0x4810, 0x4810, 0x4810, 0x47e0],   # 98 b
    ch99 = [0x47e0, 0x4810, 0x4810, 0x4810, 0x4420],           # 99 c
    ch100 = [0x47e0, 0x4810, 0x4810, 0x4810, 0x4420, 0x4ffc],  # 100 d
    ch101 = [0x47e0, 0x4890, 0x4890, 0x4890, 0x4890, 0x44e0],  # 101 e
    ch102 = [0x4010, 0x4ff8, 0x4014, 0x4014],                  # 102 f
    ch103 = [0x63f0, 0x6408, 0x6408, 0x6408, 0x6210, 0x7ff8],  # 103 g
    ch104 = [0x4ffc, 0x4020, 0x4010, 0x4010, 0x4010, 0x4fe0],  # 104 h
    ch105 = [0x4ff4],                                          # 105 i
    ch106 = [0x6000, 0x7ff4],                                  # 106 j
    ch107 = [0x4ffc, 0x4100, 0x4080, 0x4140, 0x4620, 0x4810],  # 107 k
    ch108 = [0x4ffc],                                          # 108 l
    ch109 = [0x4ff0, 0x4020, 0x4010, 0x4010, 0x4fe0, 0x4020,
            0x4010, 0x4010, 0x4fe0],                           # 109 m
    ch110 = [0x4ff0, 0x4020, 0x4010, 0x4010, 0x4010, 0x4fe0],  # 110 n
    ch111 = [0x47e0, 0x4810, 0x4810, 0x4810, 0x4810, 0x47e0],  # 111 o
    ch112 = [0x7ff8, 0x4420, 0x4810, 0x4810, 0x4810, 0x47e0],  # 112 p
    ch113 = [0x47e0, 0x4810, 0x4810, 0x4810, 0x4420, 0x7ff8],  # 113 q
    ch114 = [0x4ff0, 0x4020, 0x4010, 0x4010],                  # 114 r
    ch115 = [0x4460, 0x4890, 0x4890, 0x4890, 0x4720],          # 115 s
    ch116 = [0x4010, 0x4ffc, 0x4810, 0x4810],                  # 116 t
    ch117 = [0x47f0, 0x4800, 0x4800, 0x4800, 0x4400, 0x4ff0],  # 117 u
    ch118 = [0x4030, 0x40c0, 0x4300, 0x4c00, 0x4300, 0x40c0,
             0x4030],                                          # 118 v
    ch119 = [0x4030, 0x43c0, 0x4c00, 0x43c0, 0x4030, 0x43c0,
             0x4c00, 0x43c0, 0x4030],                          # 119 w
    ch120 = [0x4810, 0x4660, 0x4180, 0x4180, 0x4660, 0x4810],  # 120 x
    ch121 = [0x4030, 0x6060, 0x6380, 0x7c00, 0x4300, 0x40c0,
             0x4030],                                          # 121 y
    ch122 = [0x4810, 0x4c10, 0x4b10, 0x48d0, 0x4830, 0x4810],  # 122 z
    ch123 = [0x4080, 0x5f7c, 0x6002],                          # 123 {
    ch124 = [0x7ffe],                                          # 124 |
    ch125 = [0x6002, 0x5f7c, 0x4080],                          # 125 }
    ch126 = [0x4080, 0x4040, 0x4040, 0x40c0, 0x4080, 0x4080,
             0x4040],                                          # 126 ~
    ch127 = [0x4ff8, 0x4808, 0x4808, 0x4808, 0x4808, 0x4808,
             0x4ff8],                                          # 127 rect
    )

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
NORON      = 0x13    # Partial Mode OFF, Normal Display mode ON

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
PIXFMT     = 0x3A    # Pixel Format Set

IFMODE     = 0xB0    # RGB Interface control (page 154)
FRMCTR1    = 0xB1    # Frame rate control (in normal mode)
FRMCTR2    = 0xB2    # Frame rate control (in idle mode)
FRMCTR3    = 0xB3    # Frame rate control (in partial mode)
INVCTR     = 0xB4    # Frame Inversion control (page 161)
PRCTR      = 0xB5    # Blanking porch control (page 162) VFP, VBP, HFP, HBP
DFUNCTR    = 0xB6
ETMOD      = 0xB7    # Entry mode set (page 168)

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
IFCTL      = 0xF6

def lcd_reset():
    rst.high()              #
    pyb.delay(1)            #
    rst.low()               #    RESET LCD SCREEN
    pyb.delay(1)            #
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
    else:
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

def lcd_set_window(x0, y0, x1, y1):
    # Column Address Set
    lcd_write_cmd(CASET)
    lcd_write_words([(x0>>8) & 0xFF, x0 & 0xFF, (y0>>8) & 0xFF, y0 & 0xFF])
    # Page Address Set
    lcd_write_cmd(PASET)
    lcd_write_words([(x1>>8) & 0xFF, x1 & 0xFF, (y1>>8) & 0xFF, y1 & 0xFF])
    # Memory Write
    lcd_write_cmd(RAMWR)

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

    ##############################################################
    #lcd_VSYNC_deinit()
    ##############################################################

    lcd_write_cmd(GAMMASET)
    lcd_write_data(0x01)

    lcd_write_cmd(ETMOD)    # Entry mode set
    lcd_write_data(0x07)

    lcd_write_cmd(SLPOUT)   # sleep mode OFF
    pyb.delay(100)
    lcd_write_cmd(LCDON)
    pyb.delay(100)

    lcd_write_cmd(RAMWR)

def lcd_VSYNC_init():
    #pass
    lcd_write_cmd(NORON)    # Normal mode ON

    lcd_write_cmd(FRMCTR3)  # Frame rate control (in partial mode)
    lcd_write_words([0x00, 0x1B])
    #                0x00          DIV[1:0] (x 1/1)
    #                      0x10    112Hz
    #                      0x1B    70Hz (Default)

    lcd_write_cmd(DFUNCTR)  # Display function control
    lcd_write_words([0x0A, 0x80, 0x27, 0x3F])
    #                      0x80                REV = "1" norm. white, ISC[3:0] = "0000" Scan cicle 17ms.
    #                            0x27          320 lines
    #                            0x03          32  lines
    #                                  0x3F    63 CLK

    lcd_write_cmd(PRCTR)
    lcd_write_words([0x72, 0x72, 0x10, 0x18])
    #                0x72                      VFP = 114 lines
    #                      0x72                VBP = 114 lines
    #                            0x10          HFP = 16 CLK
    #                                  0x18    HBP = 24 CLK

    lcd_write_cmd(IFMODE)    # RGB Interface Signal Control
    lcd_write_data(0xE0)     # SYNC mode RCM[1:0] = "11"
    pyb.delay(16)

def lcd_VSYNC_start():
    # Set GRAM Address:
    #lcd_set_window(0, 100, 240, 108)
    #lcd_set_window(0, 0, 240, 320)

    # Interface Control:
    lcd_write_cmd(IFCTL)
    lcd_write_words([0x01, 0x00, 0x08])
    #                            0x08    DM[1:0] = "10" VSYNC mode

    pyb.delay(16)

    lcd_write_cmd(RAMWR)

# useless function
def lcd_VSYNC_deinit():
    lcd_write_cmd(IFMODE)   # RGB Interface control
    lcd_write_data(0x80)    # RCM[1:0] = "10" DE mode

    lcd_write_cmd(PTLON)    # Partial mode ON

    #lcd_write_cmd(FRMCTR3)  # Frame rate control (in partial mode)
    #lcd_write_words([0x00, 0x1b])
    #                0x00          DIV[1:0] (x 1/1)
    #                      0x1B    70Hz (Default)

    #lcd_write_cmd(DFUNCTR)  # Display function control
    #lcd_write_words([0x0A, 0x80, 0x27, 0x00])
    #                      0x80                REV = "1" norm. white, ISC[3:0] = "0000" Scan cicle 17ms.

    lcd_write_cmd(PRCTR)
    lcd_write_words([0x02, 0x02, 0x0A, 0x14])
    #                0x02                      VFP = 2 lines
    #                      0x02                VBP = 2 lines
    #                            0x0A          HFP = 10 CLK
    #                                  0x14    HBP = 20 CLK

    lcd_write_cmd(IFCTL)    # Interface Control
    lcd_write_words([0x01, 0x00, 0x00])
    #                            0x00     DM[1:0] = "00" and RM = 0 is System interface mode
    pyb.delay(16)

def get_Npix_monoword(color, pixels=4):
    R, G, B = color
    fmt = '>Q' if pixels == 4 else '>H'
    pixel = (R<<11) | (G<<5) | B
    if pixels == 4:
        monocolor = pixel<<(16*3) | pixel<<(16*2) | pixel<<16 | pixel
    elif pixels == 1:
        monocolor = pixel
    else:
        raise ValueError("Pixels count must be 1 or 4")

    word = struct.pack(fmt, monocolor)
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

def lcd_draw_pixel(x, y, color):
    lcd_set_window(x, x+1, y, y+1)
    lcd_write_data(get_Npix_monoword(color))

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

def lcd_draw_circle(x, y, radius, color, border=1):
    width = height = border
    for i in range(360):
        X = get_x_perimeter_point(x, i, radius-border)
        Y = get_y_perimeter_point(y, i, radius-border)
        if i == 90: X = X-1
        elif i == 180: Y = Y-1
        if border < 4:
            lcd_draw_pixel(X, Y, color)
        else:
            lcd_draw_rect(X, Y, width, height, color, border=0)

def lcd_draw_oval(x, y, xradius, yradius, color):
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

def set_word_length(word):
    return bin(word)[3:]

# optimize:
def lcd_fill_bicolor(data, x, y, width, height, color, bgcolor=WHITE, scale=1):
    lcd_set_window(x, x+height-1, y, y+width-1)
    bgpixel = get_Npix_monoword(bgcolor, pixels=1)
    pixel = get_Npix_monoword(color, pixels=1)
    word = ''.join(map(set_word_length, data))
    words = bytes(word, 'ascii').replace(b'0', bgpixel).replace(b'1', pixel)
    lcd_write_data(words)

def set_char_orientation():
    lcd_write_cmd(MADCTL)   # Memory Access Control
    # | MY=1 | MX=1 | MV=1 | ML=1 | BGR=1 | MH=1 | 0 | 0 |
    lcd_write_data(0xE8)

def set_graph_orientation():
    lcd_write_cmd(MADCTL)   # Memory Access Control
    # | MY=0 | MX=1 | MV=0 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
    lcd_write_data(0x48)

# optimize:
def lcd_print_char(char, x, y, color, font=Arial_14, bgcolor=BLACK, cont=False):
    index = 'ch' + str(ord(char))
    datawidth = len(font[index])
    width  = font['width']
    height = font['height']
    data   = font[index]
    X = TFTHEIGHT-y-height
    Y = x
    set_char_orientation()
    lcd_fill_bicolor(data, X, Y, datawidth, height, color, bgcolor)
    if not cont:
        set_graph_orientation()

@micropython.asm_thumb
def asm_get_charpos(r0, r1, r2):
    mul(r0, r1)
    adc(r0, r2)

def lcd_print_chars(color, font=Arial_14, bgcolor=WHITE, scale=1):
    y = 7
    x = 7
    for i in range(33, 128):
        chrwidth = len(font['ch' + str(i)])
        cont = False if i == 127 else True
        lcd_print_char(chr(i), x, y, color, bgcolor=bgcolor, cont=cont)
        x += asm_get_charpos(chrwidth, scale, 3)
        if x > (TFTWIDTH-10):
            x = 10
            y = asm_get_charpos(font['height'], scale, y)

# optimize:
def lcd_print_ln(string, x, y, color, font=Arial_14, bgcolor=WHITE, scale=1):
    for i in range(len(string)):
        chrwidth = len(font['ch' + str(ord(string[i]))])
        cont = False if i == len(string)-1 else True
        lcd_print_char(string[i], x, y, color, bgcolor=bgcolor, cont=cont)
        x += asm_get_charpos(chrwidth, scale, 3)
        if x > (TFTWIDTH-10):
            x = 10
            y -= font['height'] * scale


starttime = pyb.micros()//1000
# TEST CODE

lcd_init()

lcd_fill_monocolor(NAVY)
lcd_print_chars(WHITE, bgcolor=NAVY)
lcd_draw_rect(5, 85, TFTWIDTH-10, 55, ORANGE, border=2, fillcolor=CYAN)
lcd_print_ln("Hello MicroPython world!", 25, 95, BLACK, bgcolor=CYAN)
lcd_print_ln("(from pyBoard)", 90, 115, BLACK, bgcolor=CYAN)


print('executed in:', (pyb.micros()//1000-starttime)/1000, 'seconds')
