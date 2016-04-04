# fillMonocolor allows to fill the screen with a color at RGB565 format.
#
from lcd import *
l = LCD( rate=21000000 ) # step down the SPI bus speed to 21 MHz may be opportune when using 150+ mm wires

# Completely fill the screen in green
l.fillMonocolor(GREEN)
 

