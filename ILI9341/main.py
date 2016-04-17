#
#    WORK IN PROGRESS
#
# lcd.py - controlling TFT LCD ILI9341
# Data transfer using 4-line Serial protocol (Series II)
# 16-bit RGB Color (R:5-bit; G:6-bit; B:5-bit)
# About 30Hz monocolor screen refresh
#
# Avaliable fonts:
#'VeraMono_10',
#'Vera_10',
#'Arial_14',
#'Vera_14',
#'VeraMono_14',
#'Pitch_14',
#'Pitch_22',
#'Vera_23',
#'VeraMono_23',
#'Heydings_23',
#'Entypo_14',
#'Entypo_23',

import os

import micropython
import pyb

from lcd import LCD
from colors import *

micropython.alloc_emergency_exception_buf(100)

imgcachedir = 'images/cache'
imgdir = 'images'

# TEST CODE
if __name__ == "__main__":

    starttime = pyb.micros()//1000

    d = LCD()

    #d.cacheAllImages()
    #d.renderImageTest()

    #d.widget(10, 10, 130, 50, PURPLE, BLUE, 'widget', font=Arial_14, upper=True)
    #d.widget(10, 100, 130, 21, PURPLE, RED, 'testing string', font=Arial_14, upper=True)
    d.fillMonocolor(YELLOW)
    #d.drawRect(5, 5, 230, 18, BLACK, fillcolor=GREEN)
    #s = d.initCh(font='VeraMono_23', color=BLACK)

    d.charsBGcolorTest(font='VeraMono_23', scale=2)


    #d.fillMonocolor(GREEN)
    #d.charsTest(color=BLACK, font='Pitch_22')

    #d.renderBmp('gradient.bmp')
    #d.setPortrait(False)
    #s.printLn("Hello, world. hobbit", 5, 5)
    #d.setPortrait(True)
    #s.printLn("Hello, hello my love, hello.", 5, 5)



    # last time executed in: 1.379 seconds
    print('executed in:', (pyb.micros()//1000-starttime)/1000, 'seconds')