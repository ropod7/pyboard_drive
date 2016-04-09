# TFT LCD driver for ILI9341 chipset

This directory contains Python code for the MicroPython PyBoard used to drive a TFT based on the ILI9341 chipset (SPI bus).

The ILI9341 is really a common chip and widely distributed, you may easily find a TFT product powered with that chipset. 

The main advantage of ILI9341 powered screen reside in the fact that your TFT + ILI9341 screen does include it own video ram. You don't have to rely on your microcontroler memory for drawing and refreshing the screen, the ILI9341 will take care of it.

This driver has been developed in Python for a LCD in portrait orientation (by default) and having the 240 pixels width and 320 pixels height (by default).

![TFT Display in portrait mode](https://github.com/mchobby/pyboard_drive/blob/master/ILI9341/examples/01_basic/05e_println.jpg "TFT display in Portrait mode")

The driver has been designed to support different orientation (landscape) and different size. 

# Under construction 

Roman (the author) did already invest lot of work in this development.

The basic drawing features are already working nicely.

Please, while exploring and testing, keep in mind that ***this driver is still under development***.

# Installing 

To use this drivers on the pyboard:

* Copy the python file available under the /ILI9341/ (directory) to your Python Board
** eg: `lcd.py`, `colors.py` , `registers.py` , etc
* Create a `images` subfolder in the root of your pyboard to store bitmap images.
** also copy the bmp files if you plan to test example script  

## Consideration for micro SDCard

If you are planing to use some bitmap to be displayed on the TFT (yes, the driver can does it!) then we ***strongly recommand to use an micro SDCard*** as storage device.

Indeed, the pyboard embedded memory (inner flash) will immediately be surged with the first image copied on the pyboard.  

# directory structure

This section will describe the arrangement of the main directories.

* ***pyboard_drive/ILI9341/*** - the place for the pyboard files (to be copied on the Pyboard)
* ***pyboard_drive/ILI9341/images/*** - the place for the pyboard deriver images (OPTIONAL: to be copied on the pyboard)
* ***pyboard_drive/ILI9341/examples/*** - A collection of samples scripts. You do not need to copy them on the pyboard. Learn them to leverage the power of the driver.
* ***pyboard_drive/ILI9341/wirings/*** - A collection of wiring between the PyBoard and various model of TFT Screens (ILI9341 powered) 

# Resources

* [ILI9341 Datasheet](https://cdn-shop.adafruit.com/datasheets/ILI9341.pdf) _stored at Adafruit Industries_

# About the author

Roman, you should leave some text here.
