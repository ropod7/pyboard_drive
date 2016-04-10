# The driver allows you to draw text (string) on the screen.
# Text drawing has the following feature:
#   * Support of various font
#   * Support for text color (and background color)
#   * Cursor blinking 
#   * Draw from position (x,y)
#
from lcd import *
from fonts.arial_14 import Arial_14
import pyb

l = LCD( rate=21000000 ) # step down the SPI bus speed to 21 MHz may be opportune when using 150+ mm wires

l.fillMonocolor( CYAN )

# Create an object that can print string on the screen
#   * initCh() create a BaseChars object which retains graphical properties about the printed string
#   * bgcolor, color: defines the background color and the text color
#   * font : Arial_14 by default allows you to define the font to use
#   * scale: scale the font (1, 2, 3)
#   * bctimes: number of time to blink the cursor (when requested) 
#
c = l.initCh(font=Arial_14, color=RED, bgcolor=CYAN)

# Print the string at position x=10, y=10
#   bc: False by default, allows to show the blinking cursor when the string is printed
#   scale: scale the font (1, 2, 3)
#
c.printLn( "Hello PyBoard", 10, 10 )
