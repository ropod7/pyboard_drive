# CharsTest is a feature of the driver allowing you to see every of the 
# characters available in a font definition .
#
#
from lcd import *

l = LCD( rate=21000000 ) # step down the SPI bus speed to 21 MHz may be opportune when using 150+ mm wires

# Draw characters in black on white background for CONFORTABLE READING.
#
# For more details about drawing internals, please see the 05c_charstest.py sample

l.fillMonocolor( WHITE )
l.charsTest( color=BLACK, bgcolor=WHITE, font=Arial_14 )

