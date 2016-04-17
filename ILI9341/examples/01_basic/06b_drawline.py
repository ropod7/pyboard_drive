# drawLine allows you to draw any kind of line on the screen. 
# 
# This example draw lot of lines on the screen and allows you
#    to evaluate the speed of drawing
#
from lcd import *

l = LCD( rate=21000000 ) # step down the SPI bus speed to 21 MHz may be opportune when using 150+ mm wires

# Draw from top to bottom                                                
for i in range( 0, 320, 8 ):
    l.drawLine( 0,0, 240, i, CYAN )
# Draw line from left to right
for i in range( 0, 240, 8 ):
    l.drawLine( 0,0, i, 320, MAGENTA )

