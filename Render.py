import machine
import time
import calib

# ASSIST FUNCTIONs

'''uLerp: intger interpolation for 10bit input and blend

uLerp is ultra simple interpolation, only by simplest archmetic for fas interpolation
'''
def uLerp(a:int, b:int, position:int):

    if a < 0 or b < 0 or position < 0:
        raise TypeError('all values must be positive numbers')
    if a > 1023 or b > 1023 or position > 1023:
        raise TypeError('values must be within range of 0-1023 ie. 10bit values')

    a += 1
    b += 1

    r1 = (1023 - position) * a
    r2 = position * b
    return (r1+r2)>>10 

def uFindInTuple(inputTuple, location, value):
    # TODO shoul I do sorting?
    for i in range(len(inputTuple)):
        if inputTuple[i][location] >= value:
            return i

    return -1

# MAIN OBJECT

class Render():
    __renderWindowMS = 5
    __PWM = 19000

    #_wbKeys = ((1, 3, 1, 1, 10), (25, 217, 167, 56, 225), (50, 425, 504, 113, 450), (75, 653, 736, 169, 675), (100, 870, 960, 225, 900))
    # key point in 8bit
   #_wbKeys = ((1, 3, 1, 1, 10), (64, 210, 265, 56, 200), (128, 425, 504, 113, 450), (191, 653, 736, 169, 675), (255, 870, 960, 225, 900))
    _wbKeys = ((1, 3, 2, 1, 10), (64, 220, 310, 56, 180), (128, 445, 580, 113, 420), (191, 653, 830, 169, 575), (255, 820, 999, 200, 900))

    _rInput = 0
    _gInput = 0
    _bInput = 0
    _wInput = 0
    _rStep = 0
    _gStep = 0
    _bStep = 0
    _wStep = 0
    _currentStep = 0
    
    _temp_sensor = None

    _tempCompEnable = True

    _r = 0
    _g = 0
    _b = 0
    _w = 0

    def __init__(self, calib, temp_sensor=None, rPin=21, gPin=19, bPin=18, wPin=4):
        # generate hardware PWM outputs per channels
        self._pwm = []
        self._pwm.append(machine.PWM(machine.Pin(rPin)))
        self._pwm.append(machine.PWM(machine.Pin(gPin)))
        self._pwm.append(machine.PWM(machine.Pin(bPin)))
        self._pwm.append(machine.PWM(machine.Pin(wPin)))
        self._pwm[0].freq(19000)

        # temp sensor
        self._temp_sensor = temp_sensor
        self._calib_input = calib
        
        # init temp calibartion
        self.genRedLut()
        
        self._calib = []
        self._calib.append(self.genWBLut(calib._1500K))
        self._calib.append(self.genWBLut(calib._2000K))
        self._calib.append(self.genWBLut(calib._2800K))
        self._calib.append(self.genWBLut(calib._3200K))
        self._calib.append(self.genWBLut(calib._4800K))
        self._calib.append(self.genWBLut(calib._5600K))
        self._calib.append(self.genWBLut(calib._7800K))
        self._calib.append(self.genWBLut(calib._10K_K))
        self._calib = tuple(self._calib)

        # initiate render function periodically
        self._timer = machine.Timer(1)
        self._timer.init(period=self.__renderWindowMS, mode=machine.Timer.PERIODIC, callback=self._render)
    

        # set the deadline for the 1st render to finish
        self._deadline = time.ticks_add(time.ticks_ms(), self.__renderWindowMS)


    def setColor(self, rIn=0, gIn=0, bIn=0, wbIn=5600):
        # get white component
        inputs = [1023,1023,1023,1023]
        inputs = [rIn*4, gIn*4, bIn*4, wbIn*4]
        lowest = min((inputs))
        # make lowest 8bit as 10bit had malloc issues
        lowest = int(lowest/4)

        wbBase = list(self._calib[calib._5600K][lowest])
        # add colors
        wbBase[0] += rIn-lowest
        wbBase[1] += gIn-lowest
        wbBase[2] += bIn-lowest
        self.pushRGBW(wbBase)

    def pushRGBW(self,tupleIn):
        #547 code value has issues
        inR = tupleIn[0]
        inG = tupleIn[1]
        inB = tupleIn[2]
        inW = tupleIn[3]

        self._rInput = self._r
        self._gInput = self._g
        self._bInput = self._b
        self._wInput = self._w

        self._r = inR
        self._g = inG
        self._b = inB
        self._w = inW

        self._rStep = abs(self._r-self._rInput)>>4
        self._gStep = abs(self._g-self._gInput)>>4
        self._bStep = abs(self._b-self._bInput)>>4
        self._wStep = abs(self._w-self._wInput)>>4

        # if the step is smaller than 1 codevalue (bitshift returns instad of -0 -> -1)
        if self._rInput > self._r:
            self._rStep *=-1
    
        if self._gInput > self._g:
            self._gStep *=-1

        if self._bInput > self._b:
            self._bStep *=-1

        if self._wInput > self._w:
            self._wStep *=-1

        self._currentStep = 0

    def genRedLut(self):
        lut= []
        for i in range(1024):
            # 0.43 codevalues per 1C base -30@ 49.9% ie 513 codevalue 
            lut.append(round(i*0.43)+513)
        self._redLut = tuple(lut)

    def genWBLut(self, wb_in):
        start_time = time.ticks_ms()
        
        #get current WB only values
        current_wb = list(self._calib_input[5*wb_in:5*(wb_in+1)])
        
        #add brightness points into the data
        current_wb[0] = (1,)+current_wb[0]
        current_wb[1] = (64,)+current_wb[1]
        current_wb[2] = (128,)+current_wb[2]
        current_wb[3] = (191,)+current_wb[3]
        current_wb[4] = (255,)+current_wb[4]
        
        #convert the calibration back into tuple
        calib = tuple(current_wb)
        #add in the code values in the input table
        out = [(0,0,0,0)]
        #gen WhiteBalance 
        for i in range(255):
            i += 1
            # find closest pair
            key = uFindInTuple(calib,0,i)
            upper = calib[key]
            lower = calib[key-1]

            # get interpolation ratio
            iRatio = int( 1023*( (i-lower[0]) / (upper[0]-lower[0]) ) )

            # interpolate values
            rOut = uLerp(lower[1],upper[1],iRatio)
            gOut = uLerp(lower[2],upper[2],iRatio) 
            bOut = uLerp(lower[3],upper[3],iRatio)
            wOut = uLerp(lower[4],upper[4],iRatio)
            # append to output
            out.append((rOut,gOut,bOut,wOut))

        out.append((calib[-1][1],calib[-1][2],calib[-1][2],calib[-1][3]))
        #self._WB5600 = tuple(out)
        
        diff = time.ticks_ms()-start_time
        print("Calibration for 5600K generated in "+str(diff)+"ms")
        
        return tuple(out) 

    def _render(self, caller):
        
        # point chaser
        localR = self._rInput+(self._rStep*self._currentStep)
        localG = self._gInput+(self._gStep*self._currentStep)
        localB = self._bInput+(self._bStep*self._currentStep)
        localW = self._wInput+(self._wStep*self._currentStep)

        # if step is smaller than 1
        if self._rStep == 0: localR = self._r
        if self._gStep == 0: localG = self._g
        if self._bStep == 0: localB = self._b
        if self._wStep == 0: localW = self._w

        # advance or reset the the stepper // TODO lambda?
        if self._currentStep == 16:
            localR = self._r
            localG = self._g #seems to crahs here sometimes...?
            localB = self._b
            localW = self._w
            self.pushRGBW((localR,localG,localB,localW))
        else:
            self._currentStep += 1

        # output
        # add 30C to adjust for the -30C starting point
        currentTemp = self._temp_sensor.read()
        compensatedRed = self._redLut[currentTemp+300]*localR>>10
        if self._tempCompEnable:
            self._pwm[0].duty(compensatedRed) # calibrate the Red CH
        else:
            self._pwm[0].duty(localW) 

        self._pwm[1].duty(localG)
        self._pwm[2].duty(localB)
        self._pwm[3].duty(localW)

        # timing information
        self._renderBudgetMS = time.ticks_diff(self._deadline, time.ticks_ms())
        self._deadline = time.ticks_add(time.ticks_ms(), self.__renderWindowMS)

