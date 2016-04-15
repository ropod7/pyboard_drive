# drawLine allows you to draw any kind of line on the screen. 
# So you could draw complex shapes and graphics.
#
#
from lcd import *

l = LCD( rate=21000000 ) # step down the SPI bus speed to 21 MHz may be opportune when using 150+ mm wires

# drawLine syntax is: 
#    drawLine( x,y,x1,y1, color )
# where
#  * x,y   - are the starting point coordonates
#  * x1,y1 - are the target point coordonates
#  * color - the color tuple (r,g,b) following RGB565 coding.
#                                                
l.drawLine( 20, 155, 121, 31, RED )                                         
l.drawLine( 121, 155, 20, 31, GREEN )                                       
l.drawLine( 20,31, 121, 31, BLUE )                                          
l.drawLine( 121,155, 20,155, ORANGE )                                       
l.drawLine( 121,31, 121,155, YELLOW ) 
l.drawLine( 20,155, 20,31, CYAN )

