# drawLine allows you to draw any kind of line on the screen. 
# 
# This example shows how to draw a chart with lines
#
from lcd import *
from math import trunc, radians, sin

l = LCD( rate=21000000 ) # step down the SPI bus speed to 21 MHz may be opportune when using 150+ mm wires

# Draw axis
l.drawLine( 0,0, 240, 0, CYAN )
l.drawLine( 120, 0, 120, 320, CYAN )

# Draw a sinus plot (in the height of the screen)
previous=None
for degree in range(0,320):
    # screen x axis = SIN, screen y axis = degrees
    point = ( trunc(120+sin(radians(degree))*120) , degree ) 
    if previous != None:
        l.drawLine( previous[0], previous[1], point[0], point[1], YELLOW )
    previous = point

