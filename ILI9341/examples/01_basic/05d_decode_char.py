# WARNING: The result of the following screen will only be
#          visible on the pyboard console connexion.
#
# Fonts is composed of characters stored within a dictionnary. 
# The dictionary key is the ascii code of the caracter (the ordinal value).
# The character himself is encoded as numerical value (one value by colum)
#   all the values (columns) being store into the list
#
# The Following sample will:
#   * Access the caracter definition for "A"
#   * Show the encoded values (list of columns) 
#   * Show the encoded values as list of bits
#       - where you can identity back the caracters 
#       - the characters is encoded with a rotation of 90 degree
#       - the non relevant bit are set to 1 (see the remarks in the code)
#
# The default driver font is Arial 14 (named Arial_14) 
#    Arial 14 has 14 points height!
#

from fonts.arial_14 import Arial_14 # Note: fonts.py is also imported by lcd.py

c = 'A'
print( "ASCII code for %s = ord('%s') = %i" % (c, c, ord(c) ) )

# The default driver font is Arial_14 (can be replace with another font) 
my_font = Arial_14

print( 'Stored information for char %s' % c )
print( my_font[ ord(c) ] ) # The key in the dictionnary is '97'  

# Decoding a character in the font
print( 'Lets decode the "%s" character information' % c )
for value in my_font[ ord(c) ]:
    print( bin( value ) )

# About resulting value
#   0b100110000000000  -> 0b1  11          
#   0b100001100000000  -> 0b1    11        
#   0b100000111000000  -> 0b1     111      
#   0b100000100111000  -> 0b1     1  111   
#   0b100000100000100  -> 0b1     1     1  
#   0b100000100111000  -> 0b1     1  111   
#   0b100000111000000  -> 0b1     111      
#   0b100001100000000  -> 0b1    11        
#   0b100110000000000  -> 0b1  11          
#
# As you can see, all the value starts with 0b1!
# Why?
# 
# We have coded an Arial 14, so 14 points height.
# The 14 rightmost bits represent this information (the A).
# The remaing bits on the left (the 15th in this case) are
#   not used... so they are to set to 1. This is why all
#   the values starts with the 15th bit at 1. 
