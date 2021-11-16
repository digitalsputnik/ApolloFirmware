'''
Toolset for calibrating the lamp
Output is DS_Render output object for driving the leds while calibrating

to start:
import calib
c = calib.calib()

1. Calibrate all intesity levels for all WB (1500K-10 000K)
c.update(c._5600K,c._intensity_100,offset=(0,0,0,0),output=Output)
c.update(c._3200K,c._intensity_75,offset=(0,0,0,0),output=Output)
    
3. Export output and copy to the calib.py line 19 LampCalibration variable
c.export()
    
4. Once saved the edit in Thonny
machine.reset()   #...will load the new calibration table

'''
import Render
import time

# Placeholder for the final calibration
LampCalibartion = ((4, 1, 0, 0), (243, 126, 0, 0), (486, 251, 0, 0), (729, 373, 0, 0), (973, 481, 0, 0), (7, 4, 0, 2), (245, 161, 0, 53), (464, 305, 0, 110), (712, 468, 0, 133), (950, 600, 0, 176), (6, 4, 0, 4), (224, 194, 0, 188), (460, 390, 0, 355), (670, 554, 0, 502), (950, 750, 0, 656), (6, 4, 0, 7), (193, 177, 0, 265), (383, 345, 0, 493), (588, 512, 0, 707), (833, 691, 0, 903), (4, 1, 0, 15), (186, 280, 55, 227), (347, 497, 100, 469), (525, 715, 150, 693), (759, 944, 201, 858), (3, 2, 1, 13), (149, 235, 60, 272), (294, 441, 120, 515), (456, 668, 196, 682), (660, 878, 246, 910), (2, 2, 2, 14), (131, 270, 106, 238), (260, 507, 206, 475), (392, 718, 295, 712), (523, 897, 380, 950), (0, 1, 2, 11), (125, 291, 137, 237), (251, 547, 264, 475), (370, 765, 378, 712), (502, 927, 477, 950))

class calib():
    #Intensity points are linear scale 0.001%, 25%, 50%, 75% 100%
    _1500K = 0
    _2000K = 1
    _2800K = 2
    _3200K = 3
    _4800K = 4
    _5600K = 5
    _7800K = 6
    _10K_K = 7

    _intensity_0 = 0
    _intensity_25 = 1
    _intensity_50 = 2
    _intensity_75 = 3
    _intensity_100 = 4

    _colorpoints = []
    _lx = []
    
    def __init__(self):
        # The **ideals** measured at DSL on 11th Nov 2021 on Apollo0003(Prototype:MockupII)
        self._colorpoints.append([(4, 1, 0, 0), (243, 126, 0, 0), (486, 251, 0, 0), (729, 373, 0, 0), (973, 481, 0, 0)])
        self._colorpoints.append([(7, 4, 0, 2), (245, 161, 0, 53), (464, 305, 0, 110), (712, 468, 0, 133), (950, 600, 0, 176)])
        self._colorpoints.append([(6, 4, 0, 4), (224, 194, 0, 188), (460, 390, 0, 355), (670, 554, 0, 502), (950, 750, 0, 656)])
        self._colorpoints.append([(6, 4, 0, 7), (193, 177, 0, 265), (383, 345, 0, 493), (588, 512, 0, 707), (833, 691, 0, 903)])
        self._colorpoints.append([(4, 1, 0, 15), (186, 280, 55, 227), (347, 497, 100, 469), (525, 715, 150, 693), (759, 944, 201, 858)])
        self._colorpoints.append([(3, 2, 1, 13), (149, 252, 64, 272), (294, 473, 127, 515), (456, 695, 191, 682), (660, 917, 255, 910)])
        self._colorpoints.append([(2, 2, 2, 14), (131, 270, 106, 238), (260, 507, 206, 475), (392, 718, 295, 712), (523, 897, 380, 950)])
        self._colorpoints.append([(0, 1, 2, 11), (125, 291, 137, 237), (251, 547, 264, 475), (370, 765, 378, 712), (502, 927, 477, 950)])
    
        self._lx.append([[26, 14400],[26,  3619, 7213,  10806, 14400]])
        self._lx.append([[113,17600],[113, 4484, 8856,  13228, 17600]])
        self._lx.append([[125,24700],[125, 6268, 12412, 18556, 24700]])
        self._lx.append([[159,26100],[159, 6644, 13129, 19614, 26100]])
        self._lx.append([[196,29300],[196, 7472, 14748, 22024, 29300]])
        self._lx.append([[190,28900],[190, 7367, 14545, 21722, 28900]])
        self._lx.append([[140,29000],[140, 7355, 14570, 21785, 29000]])
        self._lx.append([[140,29600],[140, 7505, 14870, 22235, 29600]])

    '''Setup

    ...is used only to set the default brightness ranges for calibration points - should stay fairly constant throughout production

    if You need to change the _lx variable create new ranges by 1st calibrating the 0 and 100 ranges for all WB
        c = calib.calib()
        c.update(c._5600K,c._intensity_100,offset=(0,0,0,0),output=Output) # keep adjusting the offset until the calibration fits the ranges
        

    '''

    def setup(self,cmd,wb=_5600K):
        if cmd=="min":
            print("use: c._lx[c._5600K][0][0] = lux value from sekonik")
            return
        
        if cmd=="max":
            print("use: c._lx[c._5600K][0][1] = lux value from sekonik")
            return
        
        if cmd=="setup":
            lux_min = self._lx[wb][0][0]
            lux_max = self._lx[wb][0][1]
            lux_range = lux_max - lux_min
            self._lx[wb][1][0] = lux_min
            self._lx[wb][1][1] = int(lux_min+lux_range*0.25)
            self._lx[wb][1][2] = int(lux_min+lux_range*0.5)
            self._lx[wb][1][3] = int(lux_min+lux_range*0.75)
            self._lx[wb][1][4] = lux_max
            
            print(str(self._lx[wb]))
        
    def update(self, lightWB, lightInt, offset=(0,0,0,0), output=None):
        #Allow 2% variablity in Lux for the key points
        brightnessLx = self._lx[lightWB][1][lightInt]
        brightnessLxVariablity = int(brightnessLx*0.02)
        print("lux range: "+str(brightnessLx-brightnessLxVariablity)+" - "+str(brightnessLx+brightnessLxVariablity))
        print("WB should be +/-10 and dUV +/-0.0010")
        
        out = []
        out.append(self._colorpoints[lightWB][lightInt][0] + offset[0])
        out.append(self._colorpoints[lightWB][lightInt][1] + offset[1])
        out.append(self._colorpoints[lightWB][lightInt][2] + offset[2])
        out.append(self._colorpoints[lightWB][lightInt][3] + offset[3])
        
        self._colorpoints[lightWB][lightInt] = tuple(out)
        print("New values R,G,B,W: "+str(self._colorpoints[lightWB][lightInt]))
        if not(output==None):
            output.pushRGBW(out)
            
    def export(self):
        out = ()
        for i in self._colorpoints:
            out += tuple(i)
        
        print(str(out))
        
    def test(self, output, time_in=0.3):
        for i in range(256):
            output.setColor(i,i,i)
            time.sleep(time_in)

    #    
    #update(_1500K,_intensity_100,offset=(0,0,0,0))
        
        

        

