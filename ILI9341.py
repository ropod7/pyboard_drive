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
    size   = [0x1E, 0x6C], # size
    width  = 0x0D, # width
    height = 0x0E, # height
    fchar  = 0x20, # first char
    chcnt  = 0x60, # char count

    # font data
    ch32 = [0x02, [0x00, 0x00, 0x00, 0x00]],             # <space> 0x20
    ch33 = [0x01, [0xFE, 0x14]],                         # 33 !
    ch34 = [0x03, [0x1E, 0x00, 0x1E, 0x00, 0x00, 0x00]], # 34 "
    ch35 = [0x08, [0x90, 0x90, 0xF8, 0x96, 0x90, 0xF8,
                   0x96, 0x90, 0x00, 0x1C, 0x00, 0x00,
                   0x1C, 0x00, 0x00, 0x00
                   ]],                                   # 35 #
    ch36 = [0x07, [0x18, 0x24, 0x22, 0xFF, 0x42, 0x42,
                   0x84, 0x08, 0x10, 0x10, 0x3C, 0x10,
                   0x08, 0x04
                   ]],                                   # 36 $
    ch37 = [0x0A, [0x1C, 0x22, 0x22, 0x1C, 0xC0, 0x30,
                   0x8C, 0x42, 0x40, 0x80, 0x00, 0x00,
                   0x10, 0x0C, 0x00, 0x00, 0x0C, 0x10,
                   0x10, 0x0C
                   ]],                                   # 37 %
    ch38 = [0x08, [0x80, 0x5C, 0x22, 0x62, 0x92, 0x0C,
                   0x80, 0x00, 0x0C, 0x10, 0x10, 0x10,
                   0x10, 0x0C, 0x08, 0x10
                   ]],                                   # 38 &
    ch39 = [0x01, [0x1E, 0x00]],                         # 39 '
    ch40 = [0x03, [0xF0, 0x0C, 0x02, 0x1C, 0x60, 0x80]], # 40 (
    ch41 = [0x03, [0x02, 0x0C, 0xF0, 0x80, 0x60, 0x1C]], # 41 )
    ch42 = [0x05, [0x04, 0x14, 0x0E, 0x14, 0x04, 0x00,
                   0x00, 0x00, 0x00, 0x00
                   ]],                                   # 42 *
    ch43 = [0x07, [0x40, 0x40, 0x40, 0xF8, 0x40, 0x40,
                   0x40, 0x00, 0x00, 0x00, 0x0C, 0x00,
                   0x00, 0x00
                   ]],                                   # 43 +
    ch44 = [0x01, [0x00, 0x70]],                         # 44 ,
    ch45 = [0x04, [0x80, 0x80, 0x80, 0x80, 0x00, 0x00,
                   0x00, 0x00
                   ]],                                   # 45 -
    ch46 = [0x01, [0x00, 0x10]],                         # 46 .
    ch47 = [0x04, [0x00, 0xC0, 0x38, 0x06, 0x18, 0x04,
                   0x00, 0x00
                   ]],                                   # 47 /
    ch48 = [0x06, [0xFC, 0x02, 0x02, 0x02, 0x02, 0xFC,
                   0x0C, 0x10, 0x10, 0x10, 0x10, 0x0C
                   ]],                                   # 48 0
    ch49 = [0x03, [0x08, 0x04, 0xFE, 0x00, 0x00, 0x1C]], # 49 1
    ch50 = [0x06, [0x0C, 0x02, 0x02, 0x82, 0x42, 0x3C,
                   0x10, 0x18, 0x14, 0x10, 0x10, 0x10]], # 50 2
    ch51 = [0x06, [0x0C, 0x02, 0x22, 0x22, 0x22, 0xDC,
                   0x0C, 0x10, 0x10, 0x10, 0x10, 0x0C]], # 51 3
    ch52 = [0x07, [0x80, 0x40, 0x30, 0x08, 0x04, 0xFE,
                   0x00, 0x04, 0x04, 0x04, 0x04, 0x04,
                   0x1C, 0x04
                   ]],                                   # 52 4
    ch53 = [0x06, [0x38, 0x16, 0x12, 0x12, 0x12, 0xE2,
                   0x0C, 0x10, 0x10, 0x10, 0x18, 0x04]], # 53 5
    ch54 = [0x06, [0xF8, 0x44, 0x22, 0x22, 0x22, 0xC4,
                   0x0C, 0x10, 0x10, 0x10, 0x10, 0x0C]], # 54 6
    ch55 = [0x06, [0x02, 0x02, 0x02, 0xE2, 0x1A, 0x06,
                   0x00, 0x00, 0x1C, 0x00, 0x00, 0x00]], # 55 7
    ch56 = [0x06, [0xDC, 0x22, 0x22, 0x22, 0x22, 0xDC,
                   0x0C, 0x10, 0x10, 0x10, 0x10, 0x0C]], # 56 8
    ch57 = [0x06, [0x3C, 0x42, 0x42, 0x42, 0x22, 0xFC,
                   0x08, 0x10, 0x10, 0x10, 0x08, 0x04]], # 57 9
    ch58 = [0x01, [0x08, 0x10]],                         # 58 :
    ch59 = [0x01, [0x08, 0x70]],                         # 59 ;
    ch60 = [0x06, [0x40, 0xA0, 0xA0, 0x10, 0x10, 0x08,
                   0x00, 0x00, 0x00, 0x04, 0x04, 0x08]], # 60 <
    ch61 = [0x06, [0x90, 0x90, 0x90, 0x90, 0x90, 0x90,
                   0x00, 0x00, 0x00, 0x00, 0x00, 0x00]], # 61 =
    ch62 = [0x06, [0x08, 0x10, 0x10, 0xA0, 0xA0, 0x40,
                   0x08, 0x04, 0x04, 0x00, 0x00, 0x00]], # 62 >
    ch63 = [0x06, [0x0C, 0x02, 0x82, 0x42, 0x22, 0x1C,
                   0x00, 0x00, 0x14, 0x00, 0x00, 0x00]], # 63 ?
    ch64 = [0x0D, [0xE0, 0x18, 0x04, 0xC4, 0x22, 0x12,
                   0x12, 0x12, 0xA2, 0x72, 0x04, 0x08,
                   0xF0, 0x0C, 0x30, 0x40, 0x4C, 0x90,
                   0x90, 0x90, 0x88, 0x9C, 0x90, 0x50,
                   0x4C, 0x20
                   ]],                                   # 64 @
    ch65 = [0x09, [0x00, 0x80, 0xE0, 0x9C, 0x82, 0x9C,
                   0xE0, 0x80, 0x00, 0x18, 0x04, 0x00,
                   0x00, 0x00, 0x00, 0x00, 0x04, 0x18]], # 65 A
    ch66 = [0x07, [0xFE, 0x22, 0x22, 0x22, 0x22, 0x22,
                   0xDC, 0x1C, 0x10, 0x10, 0x10, 0x10,
                   0x10, 0x0C
                   ]],                                   # 66 B
    ch67 = [0x08, [0xF8, 0x04, 0x02, 0x02, 0x02, 0x02,
                   0x04, 0x08, 0x04, 0x08, 0x10, 0x10,
                   0x10, 0x10, 0x08, 0x04
                   ]],                                   # 67 C
    ch68 = [0x08, [0xFE, 0x02, 0x02, 0x02, 0x02, 0x02,
                   0x04, 0xF8, 0x1C, 0x10, 0x10, 0x10,
                   0x10, 0x10, 0x08, 0x04
                   ]],                                   # 68 D
    ch69 = [0x07, [0xFE, 0x22, 0x22, 0x22, 0x22, 0x22,
                   0x22, 0x1C, 0x10, 0x10, 0x10, 0x10,
                   0x10, 0x10
                   ]],                                   # 69 E
    ch70 = [0x07, [0xFE, 0x22, 0x22, 0x22, 0x22, 0x22,
                   0x02, 0x1C, 0x00, 0x00, 0x00, 0x00,
                   0x00, 0x00
                   ]],                                   # 70 F
    ch71 = [0x09, [0xF8, 0x04, 0x02, 0x02, 0x02, 0x42,
                   0x42, 0x44, 0xC8, 0x04, 0x08, 0x10,
                   0x10, 0x10, 0x10, 0x10, 0x08, 0x04]], # 71 G
    ch72 = [0x07, [0xFE, 0x20, 0x20, 0x20, 0x20, 0x20,
                   0xFE, 0x1C, 0x00, 0x00, 0x00, 0x00,
                   0x00, 0x1C
                   ]],                                   # 72 H
    ch73 = [0x01, [0xFE, 0x1C]],                         # 73 I
    ch74 = [0x05, [0x00, 0x00, 0x00, 0x00, 0xFE, 0x0C,
                   0x10, 0x10, 0x10, 0x0C
                   ]],                                   # 74 J
    ch75 = [0x08, [0xFE, 0x80, 0x40, 0x20, 0x50, 0x88,
                   0x04, 0x02, 0x1C, 0x00, 0x00, 0x00,
                   0x00, 0x04, 0x08, 0x10
                   ]],                                   # 75 K
    ch76 = [0x07, [0xFE, 0x00, 0x00, 0x00, 0x00, 0x00,
                   0x00, 0x1C, 0x10, 0x10, 0x10, 0x10,
                   0x10, 0x10
                   ]],                                   # 76 L
    ch77 = [0x09, [0xFE, 0x0C, 0x30, 0xC0, 0x00, 0xC0,
                   0x30, 0x0C, 0xFE, 0x1C, 0x00, 0x00,
                   0x04, 0x18, 0x04, 0x00, 0x00, 0x1C]], # 77 M
    ch78 = [0x07, [0xFE, 0x04, 0x18, 0x60, 0x80, 0x00,
                   0xFE, 0x1C, 0x00, 0x00, 0x00, 0x04,
                   0x08, 0x1C
                   ]],                                   # 78 N
    ch79 = [0x09, [0xF8, 0x04, 0x02, 0x02, 0x02, 0x02,
                   0x02, 0x04, 0xF8, 0x04, 0x08, 0x10,
                   0x10, 0x10, 0x10, 0x10, 0x08, 0x04]], # 79 O
    ch80 = [0x07, [0xFE, 0x42, 0x42, 0x42, 0x42, 0x42,
                   0x3C, 0x1C, 0x00, 0x00, 0x00, 0x00,
                   0x00, 0x00
                   ]],                                   # 80 P
    ch81 = [0x09, [0xF8, 0x04, 0x02, 0x02, 0x02, 0x02,
                   0x02, 0x04, 0xF8, 0x04, 0x08, 0x10,
                   0x10, 0x10, 0x14, 0x08, 0x1C, 0x10]], # 81 Q
    ch82 = [0x08, [0xFE, 0x42, 0x42, 0x42, 0xC2, 0x42,
                   0x42, 0x3C, 0x1C, 0x00, 0x00, 0x00,
                   0x00, 0x04, 0x08, 0x10
                   ]],                                   # 82 R
    ch83 = [0x07, [0x1C, 0x22, 0x22, 0x22, 0x42, 0x42,
                   0x8C, 0x0C, 0x10, 0x10, 0x10, 0x10,
                   0x10, 0x0C
                   ]],                                   # 83 S
    ch84 = [0x07, [0x02, 0x02, 0x02, 0xFE, 0x02, 0x02,
                   0x02, 0x00, 0x00, 0x00, 0x1C, 0x00,
                   0x00, 0x00
                   ]],                                   # 84 T
    ch85 = [0x07, [0xFE, 0x00, 0x00, 0x00, 0x00, 0x00,
                   0xFE, 0x04, 0x08, 0x10, 0x10, 0x10,
                   0x08, 0x04
                   ]],                                   # 85 U
    ch86 = [0x09, [0x06, 0x18, 0x60, 0x80, 0x00, 0x80,
                   0x60, 0x18, 0x06, 0x00, 0x00, 0x00,
                   0x04, 0x18, 0x04, 0x00, 0x00, 0x00]], # 86 V
    ch87 = [0x0D, [0x06, 0x38, 0xC0, 0x00, 0xC0, 0x3C,
                   0x02, 0x3C, 0xC0, 0x00, 0xC0, 0x38,
                   0x06, 0x00, 0x00, 0x04, 0x18, 0x04,
                   0x00, 0x00, 0x00, 0x04, 0x18, 0x04,
                   0x00, 0x00
                   ]],                                   # 87 W
    ch88 = [0x08, [0x02, 0x0C, 0x90, 0x60, 0x60, 0x90,
                   0x0C, 0x02, 0x10, 0x0C, 0x00, 0x00,
                   0x00, 0x04, 0x0C, 0x10
                   ]],                                   # 88 X
    ch89 = [0x09, [0x02, 0x04, 0x18, 0x20, 0xC0, 0x20,
                   0x18, 0x04, 0x02, 0x00, 0x00, 0x00,
                   0x00, 0x1C, 0x00, 0x00, 0x00, 0x00]], # 89 Y
    ch90 = [0x08, [0x00, 0x02, 0x82, 0x42, 0x22, 0x1A,
                   0x06, 0x02, 0x10, 0x18, 0x14, 0x10,
                   0x10, 0x10, 0x10, 0x10
                   ]],                                   # 90 Z
    ch91 = [0x02, [0xFE, 0x02, 0xFC, 0x80]],             # 91 [
    ch92 = [0x04, [0x06, 0x38, 0xC0, 0x00, 0x00, 0x00,
                   0x04, 0x18
                   ]],                                   # 92 \
    ch93 = [0x02, [0x02, 0xFE, 0x80, 0xFC]],             # 93 ]
    ch94 = [0x05, [0x20, 0x1C, 0x02, 0x1C, 0x20, 0x00,
                   0x00, 0x00, 0x00, 0x00
                   ]],                                   # 94 ^
    ch95 = [0x08, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                   0x00, 0x00, 0x80, 0x80, 0x80, 0x80,
                   0x80, 0x80, 0x80, 0x80
                   ]],                                   # 95 _
    ch96 = [0x02, [0x02, 0x04, 0x00, 0x00]],             # 96 `
    ch97 = [0x06, [0x10, 0x88, 0x48, 0x48, 0x48, 0xF0,
                   0x0C, 0x10, 0x10, 0x10, 0x08, 0x1C]], # 97 a
    ch98 = [0x06, [0xFE, 0x10, 0x08, 0x08, 0x08, 0xF0,
                   0x1C, 0x08, 0x10, 0x10, 0x10, 0x0C]], # 98 b
    ch99 = [0x05, [0xF0, 0x08, 0x08, 0x08, 0x10, 0x0C,
                   0x10, 0x10, 0x10, 0x08
                   ]],                                   # 99 c
    ch100 = [0x06, [0xF0, 0x08, 0x08, 0x08, 0x10, 0xFE,
                    0x0C, 0x10, 0x10, 0x10, 0x08, 0x1C]], # 100 d
    ch101 = [0x06, [0xF0, 0x48, 0x48, 0x48, 0x48, 0x70,
                    0x0C, 0x10, 0x10, 0x10, 0x10, 0x08]], # 101 e
    ch102 = [0x04, [0x08, 0xFC, 0x0A, 0x0A, 0x00, 0x1C,
                    0x00, 0x00
                    ]],                                   # 102 f
    ch103 = [0x06, [0xF0, 0x08, 0x08, 0x08, 0x10, 0xF8,
                    0x4C, 0x90, 0x90, 0x90, 0x88, 0x7C]], # 103 g
    ch104 = [0x06, [0xFE, 0x10, 0x08, 0x08, 0x08, 0xF0,
                    0x1C, 0x00, 0x00, 0x00, 0x00, 0x1C]], # 104 h
    ch105 = [0x01, [0xFA, 0x1C]],                         # 105 i
    ch106 = [0x02, [0x00, 0xFA, 0x80, 0x7C]],             # 106 j
    ch107 = [0x06, [0xFE, 0x80, 0x40, 0xA0, 0x10, 0x08,
                    0x1C, 0x00, 0x00, 0x00, 0x0C, 0x10]], # 107 k
    ch108 = [0x01, [0xFE, 0x1C]],                         # 108 l
    ch109 = [0x09, [0xF8, 0x10, 0x08, 0x08, 0xF0, 0x10,
                    0x08, 0x08, 0xF0, 0x1C, 0x00, 0x00,
                    0x00, 0x1C, 0x00, 0x00, 0x00, 0x1C]], # 109 m
    ch110 = [0x06, [0xF8, 0x10, 0x08, 0x08, 0x08, 0xF0,
                    0x1C, 0x00, 0x00, 0x00, 0x00, 0x1C]], # 110 n
    ch111 = [0x06, [0xF0, 0x08, 0x08, 0x08, 0x08, 0xF0,
                    0x0C, 0x10, 0x10, 0x10, 0x10, 0x0C]], # 111 o
    ch112 = [0x06, [0xF8, 0x10, 0x08, 0x08, 0x08, 0xF0,
                    0xFC, 0x08, 0x10, 0x10, 0x10, 0x0C]], # 112 p
    ch113 = [0x06, [0xF0, 0x08, 0x08, 0x08, 0x10, 0xF8,
                    0x0C, 0x10, 0x10, 0x10, 0x08, 0xFC]], # 113 q
    ch114 = [0x04, [0xF8, 0x10, 0x08, 0x08, 0x1C, 0x00,
                    0x00, 0x00
                    ]],                                   # 114 r
    ch115 = [0x05, [0x30, 0x48, 0x48, 0x48, 0x90, 0x08,
                    0x10, 0x10, 0x10, 0x0C
                    ]],                                   # 115 s
    ch116 = [0x04, [0x08, 0xFE, 0x08, 0x08, 0x00, 0x1C,
                    0x10, 0x10
                    ]],                                   # 116 t
    ch117 = [0x06, [0xF8, 0x00, 0x00, 0x00, 0x00, 0xF8,
                    0x0C, 0x10, 0x10, 0x10, 0x08, 0x1C]], # 117 u
    ch118 = [0x07, [0x18, 0x60, 0x80, 0x00, 0x80, 0x60,
                    0x18, 0x00, 0x00, 0x04, 0x18, 0x04,
                    0x00, 0x00
                    ]],                                   # 118 v
    ch119 = [0x09, [0x18, 0xE0, 0x00, 0xE0, 0x18, 0xE0,
                    0x00, 0xE0, 0x18, 0x00, 0x04, 0x18,
                    0x04, 0x00, 0x04, 0x18, 0x04, 0x00]], # 119 w
    ch120 = [0x06, [0x08, 0x30, 0xC0, 0xC0, 0x30, 0x08,
                    0x10, 0x0C, 0x00, 0x00, 0x0C, 0x10]], # 120 x
    ch121 = [0x07, [0x18, 0x60, 0x80, 0x00, 0x80, 0x60,
                    0x18, 0x00, 0x80, 0x8C, 0x70, 0x0C,
                    0x00, 0x00
                    ]],                                   # 121 y
    ch122 = [0x06, [0x08, 0x08, 0x88, 0x68, 0x18, 0x08,
                    0x10, 0x18, 0x14, 0x10, 0x10, 0x10]], # 122 z
    ch123 = [0x03, [0x80, 0x7C, 0x02, 0x00, 0x7C, 0x80]], # 123 {
    ch124 = [0x01, [0xFE, 0xFC]],                         # 124 |
    ch125 = [0x03, [0x02, 0x7C, 0x80, 0x80, 0x7C, 0x00]], # 125 }
    ch126 = [0x07, [0x40, 0x20, 0x20, 0x60, 0x40, 0x40,
                    0x20, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00
                    ]],                                   # 126 ~
    ch127 = [0x07, [0xFC, 0x04, 0x04, 0x04, 0x04, 0x04,
                    0xFC, 0x1C, 0x10, 0x10, 0x10, 0x10,
                    0x10, 0x1C
                    ]],                                   # 127
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
    lcd_write_cmd(MADCTL)   # Memory Access Control
    # | MY=0 | MX=1 | MV=0 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
    lcd_write_data(0x48)

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
        rows   = (height>>5)

        word = get_Npix_monoword(fillcolor) * pixels

        if rows < 1:
            lcd_write_data(word)
        else:
            i=0
            while i < (rows):
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

def lcd_draw_circle_filled(x, y, radius, color, border=2):
    tempY = 0
    for i in range(180):
        xNeg = get_x_perimeter_point(x, 360-i, radius)
        xPos = get_x_perimeter_point(x, i, radius)
        Y    = get_y_perimeter_point(y, i, radius)
        if i > 89: Y = Y-1
        if i == 90: xPos = xPos-1
        if tempY != Y and tempY > 0:
            length = xPos+1
            lcd_draw_Hline(xNeg, Y, length, color, width=2)
        tempY = Y

def lcd_draw_circle(x, y, radius, color, border=1):
    width = height = border
    for i in range(360):
        X = get_x_perimeter_point(x, i, radius)
        Y = get_y_perimeter_point(y, i, radius)
        if i == 90: X = X-1
        elif i == 180: Y = Y-1
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

# useless function
def lcd_pack_VSYNC_data(color):
    lcd_VSYNC_deinit()
    page = get_Npix_monoword(color)*60*32
    DOTCLK = get_Npix_monoword(BLACK)*120
    lcd_VSYNC_init()
    lcd_VSYNC_start()
    lcd_write_data(page+DOTCLK)

# Read display signal mode
def lcd_get_RDDSM():
    data = lcd_write_cmd(RDDSM, recv=True)
    data = bin(struct.unpack('>BBB', data)[1]), bin(struct.unpack('>BBB', data)[2])
    print(data)

# TODO: Set font structure for '}', '{', '@', '_' and check others
# and optimize:
def lcd_fill_bicolor(data, x, y, width, height, color, bgcolor=BLACK):
    lcd_set_window(x, x+height-1, y, y+width-1)
    words = bytearray(0)
    bgpixel = get_Npix_monoword(bgcolor, pixels=1)
    pixel = get_Npix_monoword(color, pixels=1)

    for word in data:
        word = bin(word)[2:] + '0'
        if len(word) < height:
            word = '0'*(height-len(word)) + word
        for io in word:
            words += bgpixel if io == '0' else pixel

    lcd_write_data(words)

# optimize:
def lcd_print_char(char, x, y, color, font=Arial_14, bgcolor=BLACK):
    index = 'ch' + str(ord(char))
    datawidth = font[index][0]
    width  = font['width']
    height = font['height']
    dt  = font[index][1]
    data = []
    j = 0
    for i in range(len(dt)):
        if i < len(dt)/2:
            data.append(dt[i])
        else:
            data[j] = ((dt[i]>>2)<<8) | data[j]
            j+=1

    # TODO: Pack MADCTL cmd to function
    lcd_write_cmd(MADCTL)   # Memory Access Control
    # | MY=1 | MX=1 | MV=1 | ML=1 | BGR=1 | MH=1 | 0 | 0 |
    lcd_write_data(0xE8)
    lcd_fill_bicolor(data, x, y, datawidth, height, color, bgcolor)
    lcd_write_cmd(MADCTL)   # Memory Access Control
    # | MY=0 | MX=1 | MV=0 | ML=0 | BGR=1 | MH=0 | 0 | 0 |
    lcd_write_data(0x48)

def lcd_print_chars(font=Arial_14):
    y = 10
    x = TFTHEIGHT-10-font['height']
    for i in range(33, 128):
        if i == 64: continue    # @ char
        lcd_print_char(chr(i), x, y, BLACK, bgcolor=LIGHTGREY)
        y+=font['width']
        if y > (TFTWIDTH-10):
            y = 10
            x -= font['height']

# optimize:
def lcd_print_ln(string, color, font=Arial_14):
    y = 10
    x = TFTHEIGHT-110-font['height']
    for i in range(len(string)):
        lcd_print_char(string[i], x, y, BLACK, bgcolor=CYAN)
        y+=font['ch'+str(ord(string[i]))][0]+3
        if y > (TFTWIDTH-10):
            y = 10
            x -= font['height']


# TEST CODE

lcd_init()

lcd_fill_monocolor(LIGHTGREY)

lcd_print_chars()
