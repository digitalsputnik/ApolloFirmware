import uasyncio as asyncio
import machine
import artnet_client
import calibration as calib
import lm75
import flags
import pysaver
import Data.pins as pins

red_pin = pins.red_pin
green_pin = pins.green_pin
blue_pin = pins.blue_pin
white_pin = pins.white_pin

is_on = pysaver.load("is_on", True)

current_color = pysaver.load("current_color", (10, 10, 10, 10))
target_color = current_color

fx_buffer = [(255,255,255)]

_pwm = []

calibration = []
red_lut = ()

temp_sensor = None
temp_comp_enabled = True

max_op_temp = 700
max_temp_reached = False

pins_enabled = False

power_status_task = None
default_color_task = None

running = False

async def __setup__():
    global _pwn, red_pin, green_pin, blue_pin, white_pin, calibration, temp_sensor, power_status_task, default_color_task, running
    artnet_client.callback = set_color
    
    power_status_task = asyncio.create_task(toggle_power_status_waiter())
    default_color_task = asyncio.create_task(set_default_color_waiter())
    
    # disable all outputs to avoid blinking during setup 
    turn_leds_off()
    
    _pwm.append(machine.PWM(machine.Pin(red_pin)))
    _pwm.append(machine.PWM(machine.Pin(green_pin)))
    _pwm.append(machine.PWM(machine.Pin(blue_pin)))
    _pwm.append(machine.PWM(machine.Pin(white_pin)))
    _pwm[0].freq(19000)
    
    generate_red_lut()
    
    calibration = []
    calibration.append(generate_wb_lut(calib._1500K))
    calibration.append(generate_wb_lut(calib._2000K))
    calibration.append(generate_wb_lut(calib._2800K))
    calibration.append(generate_wb_lut(calib._3200K))
    calibration.append(generate_wb_lut(calib._4800K))
    calibration.append(generate_wb_lut(calib._5600K))
    calibration.append(generate_wb_lut(calib._7800K))
    calibration.append(generate_wb_lut(calib._10K_K))
    calibration = tuple(calibration)
    
    running = True

async def __loop__():
    global _pwm, current_color, target_color, temp_comp_enabled, pins_enabled, max_op_temp, max_temp_reached, is_on, running
    
    if not max_temp_reached and running:
        vector = (target_color[0]-current_color[0], target_color[1]-current_color[1], target_color[2]-current_color[2], target_color[3]-current_color[3])
        current_color = [int(current_color[0] + vector[0]*0.1), int(current_color[1] + vector[1]*0.1), int(current_color[2] + vector[2]*0.1), int(current_color[3] + vector[3]*0.1)]
        
        diff = (target_color[0]-current_color[0], target_color[1]-current_color[1], target_color[2]-current_color[2], target_color[3]-current_color[3])
        
        if (abs(diff[0]) < 10):
            current_color[0] = int(target_color[0])
            
        if (abs(diff[1]) < 10):
            current_color[1] = int(target_color[1])
            
        if (abs(diff[2]) < 10):
            current_color[2] = int(target_color[2])
            
        if (abs(diff[3]) < 10):
            current_color[3] = int(target_color[3])
            
        current_color = tuple(current_color)

        current_temp = lm75.current_temp
    
        if current_temp > (1022-300):
            current_temp = 1022-300
        if current_temp < 0:
            current_temp = 0
    
        compensatedRed = red_lut[current_temp+300]*current_color[0]>>10
        if temp_comp_enabled:
            _pwm[0].duty(compensatedRed) # calibrate the Red CH
        else:
            _pwm[0].duty(current_color[0]) 
    
        _pwm[1].duty(current_color[1])
        _pwm[2].duty(current_color[2])
        _pwm[3].duty(current_color[3])
    
        if (not pins_enabled and is_on):
            pins_enabled = True
            turn_leds_on()
        
#         if (current_temp > max_op_temp):
#             turn_leds_off()
#             is_on = False
#             max_temp_reached = True

async def toggle_power_status_waiter():
    global is_on, current_color, pins_enabled, max_temp_reached
    while True:
        await flags.power_short_flag.wait()
        
        if not max_temp_reached and running:
            is_on = not is_on
        
            if is_on:
                if (not pins_enabled):
                    pins_enabled = True
                turn_leds_on()
                pysaver.save("is_on", is_on)
            else:
                turn_leds_off()
                pysaver.save("current_color", current_color)
                pysaver.save("is_on", is_on)
            
async def set_default_color_waiter():
    global is_on
    while True:
        await flags.power_long_flag.wait()
        
        if not max_temp_reached and running:
            if not is_on:
                is_on = True
                turn_leds_on()
        
            set_color(255,255,255,123)

def turn_leds_off():
    machine.Pin(27, machine.Pin.OUT, value=0)
    
def turn_leds_on():
    machine.Pin(27, machine.Pin.OUT, value=1)

def set_color(r_in=0, g_in=0, b_in=0, wb_in=0, fx_in=0):
    global target_color, max_temp_reached, is_on
    
    if not max_temp_reached and is_on:
        
        print("before - " + str((r_in, g_in, b_in)))
        
        r_in = r_in * ((255 - fx_in) / 255)
        g_in = g_in * ((255 - fx_in) / 255)
        b_in = b_in * ((255 - fx_in) / 255)
        
        r_in += fx_buffer[0][0] * (fx_in / 255)
        g_in += fx_buffer[0][1] * (fx_in / 255)
        b_in += fx_buffer[0][2] * (fx_in / 255)
        
        r_in = int(r_in)
        g_in = int(g_in)
        b_in = int(b_in)
        
        print("after - " + str((r_in, g_in, b_in)))
        
        inputs = [r_in*4, g_in*4, b_in*4]
        lowest = min((inputs))
        # make lowest 8bit as 10bit had malloc issues
        lowest = int(lowest/4)
    
        wb_in = wb_in*33.33334+1500
        
        ranges = [500,800,400,1600,800,2200,2200]
        values = [1500,2000,2800,3200,4800,5600,7800,10000]
        
        temp_base = calib._1500K
        
        if wb_in>=2000:
            temp_base = calib._2000K
        if wb_in>=2800:
            temp_base = calib._2800K
        if wb_in>=3200:
            temp_base = calib._3200K
        if wb_in>=4800:
            temp_base = calib._4800K
        if wb_in>=5600:
            temp_base = calib._5600K
        if wb_in>=7800:
            temp_base = calib._7800K
        
        # to avoid overflow
        if wb_in > 10000:
            wb_in = 10000
        
        overflow = wb_in-values[temp_base]
        overflow1024 = int(overflow/ranges[temp_base]*1023)
        
        wbBaseA = list(calibration[temp_base][lowest])
        wbBaseB = list(calibration[temp_base+1][lowest])
        
        wbBase = [0,0,0,0]
        wbBase[0] = lerp(wbBaseA[0],wbBaseB[0],overflow1024)
        wbBase[1] = lerp(wbBaseA[1],wbBaseB[1],overflow1024)
        wbBase[2] = lerp(wbBaseA[2],wbBaseB[2],overflow1024)
        wbBase[3] = lerp(wbBaseA[3],wbBaseB[3],overflow1024)
        
        # add colors
        wbBase[0] += r_in-lowest
        wbBase[1] += g_in-lowest
        wbBase[2] += b_in-lowest
        
        target_color = (wbBase[0], wbBase[1], wbBase[2], wbBase[3])
    
def generate_red_lut():
    global red_lut
    lut= []
    for i in range(1024):
        # 0.43 codevalues per 1C base -30@ 49.9% ie 513 codevalue 
        lut.append(round(i*0.43)+513)
    red_lut = tuple(lut)
    
def generate_wb_lut(wb_in):
    current_wb = list(calib.lamp_calibration[5*wb_in:5*(wb_in+1)])

    current_wb[0] = (1,)+current_wb[0]
    current_wb[1] = (64,)+current_wb[1]
    current_wb[2] = (128,)+current_wb[2]
    current_wb[3] = (191,)+current_wb[3]
    current_wb[4] = (255,)+current_wb[4]
        
    current_calib = tuple(current_wb)
    
    out = [(0,0,0,0)]
    
    for i in range(255):
        i += 1
        
        key = find_in_tuple(current_calib,0,i)
        upper = current_calib[key]
        lower = current_calib[key-1]

        i_ratio = int( 1023*( (i-lower[0]) / (upper[0]-lower[0]) ) )

        r_out = lerp(lower[1],upper[1],i_ratio)
        g_out = lerp(lower[2],upper[2],i_ratio) 
        b_out = lerp(lower[3],upper[3],i_ratio)
        w_out = lerp(lower[4],upper[4],i_ratio)
        
        out.append((r_out,g_out,b_out,w_out))

    out.append((current_calib[-1][1],current_calib[-1][2],current_calib[-1][2],current_calib[-1][3]))
        
    print("Calibration for " + calib._lut[wb_in] + " generated")
        
    return tuple(out)

# Helpers

def find_in_tuple(inputTuple, location, value):
    for i in range(len(inputTuple)):
        if inputTuple[i][location] >= value:
            return i

    return -1

def lerp(a:int, b:int, position:int):

    if a < 0 or b < 0 or position < 0:
        raise TypeError('all values must be positive numbers')
    if a > 1023 or b > 1023 or position > 1023:
        raise TypeError('values must be within range of 0-1023 ie. 10bit values')

    a += 1
    b += 1

    r1 = (1023 - position) * a
    r2 = position * b
    return (r1+r2)>>10 