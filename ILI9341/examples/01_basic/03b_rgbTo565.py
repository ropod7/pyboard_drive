# If you did read the "About Color" file, you do know that color must be coded with RGB565
#    5 bit for Red, 6 bit for Green, 5 bit for Blue.
#
# Most common RGB coding is using RGB888 (8 bits for each color)
#
# In this sample, we will use a color converter to draw a green color fading based on the 
# w3schools color picker (from #00ff00 -> ffffff, so from RGB 0,255,0 -> 255,255,255 ) 
#
from lcd import *
import pyb
l = LCD( rate=21000000 ) # step down the SPI bus speed to 21 MHz may be opportune when using 150+ mm wires

# Using color convertion from RGB888 to RGB565
colorStep = 11        # jump 8 bits color by 11
boxes = 255//colorStep # We will draw x boxes
for i in range( 0, boxes+1 ):
    iColorValue = i * colorStep
    aColor = rgbTo565(iColorValue,255,iColorValue)
    yStart = 0+i*(320//boxes)
    yHeight = 320//boxes
    print( '%i, %i = %i' % (yStart, yHeight, yStart+yHeight) )
    l.drawRect( 0, yStart, 240, yHeight, aColor, border=1, fillcolor=aColor )

pyb.delay( 5000 ) # Wait for 5 sec

for i in range( 0, boxes+1 ):
    iColorValue = i * colorStep
    aColor = rgbTo565(iColorValue,iColorValue, 255)
    yStart = 0+i*(320//boxes)
    yHeight = 320//boxes
    print( '%i, %i = %i' % (yStart, yHeight, yStart+yHeight) )
    l.drawRect( 0, yStart, 240, yHeight, aColor, border=1, fillcolor=aColor )

pyb.delay( 5000 ) # Wait for 5 sec

for i in range( 0, boxes+1 ):
    iColorValue = i * colorStep
    aColor = rgbTo565(255,iColorValue,iColorValue)
    yStart = 0+i*(320//boxes)
    yHeight = 320//boxes
    print( '%i, %i = %i' % (yStart, yHeight, yStart+yHeight) )
    l.drawRect( 0, yStart, 240, yHeight, aColor, border=1, fillcolor=aColor )


