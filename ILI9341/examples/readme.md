# Introduction

This sections contains many example showing how to use the capabilities of the screen driver.

The examples are structured as follows:
* ***01_basic*** - All examples related to the basic drawing feature of the driver

# How to run examples

First of all, you have to copy the driver code on your MicroPython Pyboard board.

All the driver files must be present in the root of your pyboard drive. Those files are presently:

1. colors.py, lcd.py, registers.py and also fonts.py
2. \images\ folder (required if you want to display pictures. pictures must be stored under \images\ )  

## main.py - The hard way 

The simplest way to test (but also the most boring with the time) is:

1. Edit the ***main.py*** file on your PyBoard.
2. Copy the example script inside the main.py file.
3. Close your editor.
4. Eject the PyBoard Drive from your computer.
5. press the "Reset" button on your pyboard.

The Pyboard will restarts and execute the script stored in "main.py"

## pyboard.py - The easiest way

Editing the main.py file again and again is quite... cumbersome. It exists a tool named "[pyboard.py](https://github.com/micropython/micropython/blob/master/tools/pyboard.py)" allowing you to send pyboard python script to execute toward the USB wire.

I do use it everyday, I strongly encourage you to get familliar with it. 

When all the needed driver files are installed on the Pyboard filesystem, you can simply send the example script from your computer toward the pyboard (in REPL mode)

The '''pyboard.py''' is executed from your computer and will get the pyboard python as parameter. 

The ***Pyboard.py*** will turn the PyBoard in RAW REPL mode, send the mentionned pyboard python script toward the USB cable and then execute that script on the Pyboard. That's ROCK!!!

   
Once ***pyboard.py*** installed on your computer, you will be able to use it by using the following syntax:

```
./pyboard.py 06a_drawline.py
```

or 

```
python pyboard.py 06a_drawline.py
```

# Live testing

With the driver files installed on the pyboard filesystem, you could use the ["pyterm.py" script form Mr Boulanger](http://wdi.supelec.fr/boulanger/MicroPython/#Pyterm) (supelec.fr).

'''pyterm.py''' allows you to establish an live REPL session with you pyboard (based on minicom, so Unix based only). 

This is quite useful to run the pyboard in interactive mode and execute statement by statement.

I did use it a lot to experiment the driver behaviors. 

_I do even modify the pyterm.py to always start on the Pyboard serial connexion ( /dev/ttyACM0 in my own case)._
