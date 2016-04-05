# CharsTest is a feature of the driver allowing you to see every of the 
# characters available in a font definition.
#
#
from lcd import *

l = LCD( rate=21000000 ) # step down the SPI bus speed to 21 MHz may be opportune when using 150+ mm wires

l.charsTest( color=YELLOW, font=Arial_14 )

