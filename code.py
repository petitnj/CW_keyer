# CW controller NJP 23 Apri 2021 uses touch for dot dash msg0 and msg1
# uses rotary encoder for CW speed
# runs on Adafruit Feather 2040 based on
# picotouch_code.py --
# 2021 - @todbot / Tod Kurt - github.com/todbot/picotouch
# on Pico / RP2040, need 1M pull-down on each  touch input
# rotary encoder has center ground and rotor to pins 5 and 6
# neopixel color based on key type
# neopixel blinks white to indicate keep alive
# key output is feather LED but could be other pins for keying


import time
import board
from digitalio import DigitalInOut, Pull, Direction
import touchio
import neopixel
import rotaryio
from adafruit_debouncer import Debouncer

rate = 15
baserate = 15
minrate = 5
maxrate = 25
dot_length = 1.6/rate
ratio = 3  # between dot and dash length
dash_length = ratio * dot_length
keyed = DigitalInOut(board.LED)
keyed.direction = Direction.OUTPUT
keygnd = DigitalInOut(board.D10)
keygnd.direction = Direction.OUTPUT
pixels = neopixel.NeoPixel(board.NEOPIXEL,1)
pixels[0] = (155,0,0)
encoder = rotaryio.IncrementalEncoder(board.D5, board.D6) # rate encoder
last_position = None
position = None
keygnd.value = True
# morse code converter dictionary o = dot, a = dash
code = { ' ':'','A': 'oa', 'B':'aooo', 'C':'aoao','D':'aoo', 'E':'o',
'F':'ooao' ,'G':'aao', 'H':'oooo','I':'oo','J':'oaaa',
'K':'aoa','L':'oaoo', 'M':'aa', 'N':'ao', 'O':'aaa','P':'ooao',
'Q':'aaoa','R':'oao','S':'ooo','T':'a','U':'ooa','V':'oooa',
'W':'oaa','X':'oaao','Y':'aoaa', 'Z':'aaoo','0':'aaaaa','1':'oaaaa',
'2':'ooaaa','3':'oooaa','4':'ooooa','5':'ooooo','6':'aoooo','7':'aaooo',
'8':'aaaoo','9':'aaaao','?':'ooaaoo',',':'aaooaa','.':'oaoaoa'}

# message0 = 'CQ CQ CQ DE WB0VGI WB0VGI WB0VGI K'  # extend these to make a full message
# message1 = 'RST 599 599 QTH HARRIS, MN HARRIS, MN OP NOEL NOEL BTU DE WB0VGI KN'
message0 = 'CQ'
message1 = 'RST'
count = 0

def adj_rate():  # set rates the first time thru
    global rate
    global dot_length
    global dash_length
    if rate > maxrate:
        rate = maxrate
    if rate < minrate:
        rate = minrate
    dot_length = 1.6/rate
    dash_length = 3.0 * dot_length
    print('CW rate ', rate, ' wpm')

def check_rotary():
    global position
    global last_position
    global rate
    position = encoder.position   # check to see if rate changed
    if position != last_position:
        rate = baserate - position # rotary connection is reversed so subtract
        adj_rate()                  # set new dot and dash length
    last_position = position


def letter(letin):  # convert a string to morse code
    for i in range(0, len(letin)):
        mcode = code[letin[i]]
        if letin[i] == '':
            print('word space')
        else:
            for j in range(0, len(mcode)):
                if mcode[j] == 'a':
                    my_dash()
                else:
                    my_dot()
            print('char space')
            time.sleep(dash_length)  # intercharacter length

def key(length):  # this is the key down command with interbit length
    global dot_length
    keyed.value = True
    keygnd.value = False  # ground to key
    time.sleep(length)
    keyed.value = False
    keygnd.value = True # True
    check_rotary()
    time.sleep(dot_length)  # inter bit length

def my_dash():
    print('dash')
    key(dash_length)

def my_dot():
    print('dot')

    key(dot_length)

def my_msg0():
    print('message 0')
    letter(message0)
def my_msg1():
    print('message 1')
    letter(message1)
touch_threshold_adjust = 500

touch_pins = (board.SDA, board.D4,board.TX,board.SCL)
# dash, dot, msg0, msg1
touch_ins = []
touchs = []
for pin in touch_pins:
    touchin = touchio.TouchIn(pin)
    touchin.threshold += touch_threshold_adjust
    touch_ins.append(touchin)
    touchs.append( Debouncer(touchin) )

while True:
    for i in range(len(touchs)):
        touch = touchs[i]
        touch.update()
        if touch.value:
            count = 0
            if i == 0:
                my_dot()
                pixels[0] = (75,0,0)
            if i == 1:
                pixels[0] = (0,50,0)
                my_dash()
            if i == 2:
                pixels[0] = (0,0,150)
                my_msg0()
            if i == 3:
                pixels[0] = (0,50,50)
                my_msg1()
            pixels[0] = (0,0,0)
    if count > 1000: # keep alive blinker
        pixels[0] = (35,35,25)
        count = 0
    else:
        pixels[0] = (0,0,0)
        count = count + 1
    check_rotary()