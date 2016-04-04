# fillMonocolor allows to fill the screen with a color at RGB565 format.
#
# Thank to the margin paramater, you can "skip a border" all around the screen border.
# The fill operation will then be centered in the screen   
#
from lcd import *
l = LCD( rate=21000000 ) # step down the SPI bus speed to 21 MHz may be opportune when using 150+ mm wires

l = LCD( rate=21000000 )
l.fillMonocolor( RED )
l.fillMonocolor( GREEN, margin=10 )
l.fillMonocolor( BLUE, margin=20 )
l.fillMonocolor( CYAN, margin=30 )
l.fillMonocolor( YELLOW, margin=40 )
l.fillMonocolor( ORANGE, margin=50 )
l.fillMonocolor( WHITE, margin=60 )
l.fillMonocolor( LIGHTGREY, margin=70 )
l.fillMonocolor( PURPLE, margin=80 ) 
 

