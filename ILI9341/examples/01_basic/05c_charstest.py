# CharsTest is a feature of the driver allowing you to see every of the 
# characters available in a font definition .
#
#
from lcd import *

l = LCD( rate=21000000 ) # step down the SPI bus speed to 21 MHz may be opportune when using 150+ mm wires

# This color configuration allows you to PROPERLY IDENTIFY THE DRAWING MECANISM on the screen.

#   * Bacground screen color is not initialised --> background is black
#   * Background  Yellow Background (allow to identify character width)
#   * Foreground  Black (to see the caharacter in its yellow matrix) 
l.charsTest( color=BLACK, font='Arial_14' )

