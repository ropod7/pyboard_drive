# fillMonocolor allows to fill the screen with a color at RGB565 format.
#
# Thank to the margin paramater, you can "skip a border" all around the screen border.
# The fill operation will then be centered in the screen   
#
from lcd import *
import pyb

l = LCD( rate=21000000 ) # step down the SPI bus speed to 21 MHz may be opportune when using 150+ mm wires

# CharsTest() simply print all the characters of a given font.
#    Quite usefull for testing.
#
# l.charsTest( color=YELLOW, font=Arial_14 )
# pyb.delay( 5000 ) 

l.fillMonocolor( CYAN )

# Create an object that can print string on the screen
#   * initCh() create a BaseChars object which retains graphical properties about the printed string
#   * bgcolor, color: defines the background color and the text color
#   * font : Arial_14 by default allows you to define the font to use
#   * scale: scale the font (1, 2, 3)
#   * bctimes: number of time to blink the cursor (when requested) 
#
c = l.initCh(color=RED, bgcolor=CYAN)

# Print the string at position x=10, y=10
#   bc: False by default, allows to show the blinking cursor when the string is printed
#   scale: scale the font (1, 2, 3)
#
c.printLn( "Hello PyBoard", 10, 10 )
