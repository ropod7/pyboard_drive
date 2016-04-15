# THIS POINT IS VERY IMPORTANT - Please take the time to read it.
#
# The ILI9341 does not use the usual RGB color coding (8 bits for each color - so 3 bytes to define a color)
# BUT RGB565 color coding (5 bits for red, 6 bit for Green,  5 bits for blue - so 2 bytes to define a color)
# 
# As a direct result of this RGB565 color coding, you will not have the 
# RED color defined as (255,0,0) like usual representation over the Net (eg: Web color).
# With RGB565, the RED color will be coded as (31, 0,  0 ).
#
# Here some of the color definition (also translated in French)
# Colors are defined in the file COLORS.PY
#
#   BLACK       = (0,  0,  0 )        # NOIR       -   0,   0,   0
#   NAVY        = (0,  0,  15)        # BLEU NAVY  -   0,   0, 128
#   DARKGREEN   = (0,  31, 0 )        # VERT FONCé -   0, 128,   0
#   DARKCYAN    = (0,  31, 15)        # CYAN FONCé -   0, 128, 128
#   MAROON      = (15, 0,  0 )        # MARRON     - 128,   0,   0
#   PURPLE      = (15, 0,  15)        # POURPRE    - 128,   0, 128
#   OLIVE       = (15, 31, 0 )        # VERT OLIVE - 128, 128,   0
#   LIGHTGREY   = (23, 47, 23)        # VERT CLAIR - 192, 192, 192
#   DARKGREY    = (15, 31, 15)        # GRIS FONCé - 128, 128, 128
#   BLUE        = (0,  0,  31)        # BLEU       -   0,   0, 255
#   GREEN       = (0,  63, 0 )        # VERT       -   0, 255,   0
#   CYAN        = (0,  63, 31)        # CYAN       -   0, 255, 255
#   RED         = (31, 0,  0 )        # ROUGE      - 255,   0,   0
#   MAGENTA     = (31, 0,  31)        # MAGENTA    - 255,   0, 255
#   YELLOW      = (31, 63, 0 )        # JAUNE      - 255, 255,   0
#   WHITE       = (31, 63, 31)        # BLANC      - 255, 255, 255
#   ORANGE      = (31, 39, 0 )        # ORANGE     - 255, 165,   0
#   GREENYELLOW = (18, 63, 4 )        # VERT/JAUNE - 173, 255,  47
#
from lcd import *
l = LCD( rate=21000000 ) # step down the SPI bus speed to 21 MHz may be opportune when using 150+ mm wires

# Define the color BLUE with RGB565 coding and store it into a tuple
aColor = (0,0,31)
l.drawPixel( 80, 130, aColor ) # x=80, y=130

# Using directly a color tuple (green) when calling a drawing function
l.drawPixel( 90, 140, (0,63,0) )

# Using one of the predefined color available in colors.py
l.drawPixel( 100, 150, YELLOW )
 

