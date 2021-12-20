import uasyncio as asyncio
import machine
import artnet_client
import calibration as calib

red_pin = 21
green_pin = 19
blue_pin = 18
white_pin = 4

current_color = (10, 10, 10, 10)
target_color = (10, 10, 10, 10)

_pwm = []

calibration = []
red_lut = ()

async def __setup__():
    global _pwn, red_pin, green_pin, blue_pin, white_pin, calibration
    artnet_client.callback = set_color
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

async def __loop__():
    global _pwm, current_color, target_color
    vector = (target_color[0]-current_color[0], target_color[1]-current_color[1], target_color[2]-current_color[2], target_color[3]-current_color[3])
    current_color = (int(current_color[0] + vector[0]*0.1), int(current_color[1] + vector[1]*0.1), int(current_color[2] + vector[2]*0.1), int(current_color[3] + vector[3]*0.1))
    _pwm[0].duty(current_color[0]) 
    _pwm[1].duty(current_color[1])
    _pwm[2].duty(current_color[2])
    _pwm[3].duty(current_color[3])

def set_color(r_in=0, g_in=0, b_in=0, wb_in=0):
    global target_color
    target_color = (r_in, g_in, b_in, wb_in)
    
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