# The driver allows you to draw text (string) on the screen.
# Text drawing has the following feature:
#   * Support of various font
#   * Support for text color (and background color)
#   * Cursor blinking 
#   * Draw from position (x,y)
#
from lcd import *
import pyb

l = LCD( rate=21000000 ) # step down the SPI bus speed to 21 MHz may be opportune when using 150+ mm wires

l.fillMonocolor( CYAN )

# Create an object that can print string on the screen
#   * initCh() create a BaseChars object which retains graphical properties about the printed string
#   * color: defines the text color
#   * font : Arial_14 by default allows you to define the font to use
#   * scale: scale the font (1, 2, 3)
#
c = l.initCh(color=RED, font='Arial_14')

# Print the string at position x=10, y=10
#   scale: scale the font (1, 2, 3)
#
c.printLn( "Hello PyBoard", 10, 10 )
