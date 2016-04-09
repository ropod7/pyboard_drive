== TFT Touch Shield ==
The TFT-Touch-Shield is an Arduino product produced by AdaFruit industries USA [2.8" TFT Touch Shield for Arduino with Resistive Touch Screen](https://www.adafruit.com/products/1651). This product is widelyyyyy distribued in the world.

The main feature are:
* 2.8", 320 x 240 pixels, ILI9341 powered (SPI bus)
* Resistive touch screen, STMPE610 (SPI bus)

***PLEASE NOTE:*** presently (on april 9, 2016) the driver does not support any touch interface.

== Wiring ==

![TFT Touch Shield wired on PyBoard]((https://github.com/mchobby/pyboard_drive/blob/master/ILI9341/wirings/tft-touch-shield/wiring.jpg "TFT Touch Shield wired on PyBoard")

The high resolution wiring is [available here on wiki.mchobby.be](http://wiki.mchobby.be/index.php?title=MicroPython-ILI9341-Brancher)

```
PyBoard                  2.8" TFT Shield for Arduino
SPI(1)                   ILI9341 (powered)
----------------------------------

Vin <----------------> 5V
GND <----------------> GND
X8 (mosi)<-----------> MOSI, #11, fils vert (green wire)
X7 (miso)<-----------> MISO, #12, fils violet (violet wire, not useful yet).
X6 (sck) <-----------> CLK, #13, fils jaune (yellow wire)

X5 (/ss) <-----------> D/C, #9, fils brun (brown wire, Data/Command)

X4 <-----------------> CS , #10, fils orange (orange wire, Chip Select)
X3 <-----------------> RST, fils gris (grey wire, Reset signal)
```
