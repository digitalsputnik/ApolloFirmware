'''
Toolset for calibrating the lamp

'''

#Intensity points are linear scale 0%, 25%, 50%, 75% 100%
_1500K = 0
_2000K = 1
_2800K = 2
_3200K = 3
_4800K = 4
_5600K = 5
_7500K = 6
_10K_K = 7

_intensity_0 = 0
_intensity_25 = 1
_intensity_50 = 2
_intensity_75 = 3
_intensity_100 = 4

_colorpoints = []
_colorpoints.append(((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)))
_colorpoints.append(((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)))
_colorpoints.append(((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)))
_colorpoints.append(((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)))
_colorpoints.append(((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)))
_colorpoints.append(((3, 2, 1, 10), (220, 310, 56, 180), (445, 580, 113, 420), (653, 830, 169, 575), (820, 999, 200, 900)))
_colorpoints.append(((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)))
_colorpoints.append(((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)))

_lx = []
_lx.append([[0,0],[0,0,0,0,0]])
_lx.append([[0,0],[0,0,0,0,0]])
_lx.append([[0,0],[0,0,0,0,0]])
_lx.append([[0,0],[0,0,0,0,0]])
_lx.append([[0,0],[0,0,0,0,0]])
_lx.append([[108,23800],[108,6031,11654,17877,23800]])
_lx.append([[0,0],[0,0,0,0,0]])
_lx.append([[0,0],[0,0,0,0,0]])

def setup(cmd,wb=5,output=Output):
    if cmd=="min":
        output.pushRGBW(_colorpoints[wb][_intensity_0])
        print("use: lx[_5600K][0][_intensity_0] = lux value from sekonik")
        return 
    if cmd=="max":
        output.pushRGBW(_colorpoints[wb][_intensity_100])
        print("use: lx[_5600K][0][_intensity_100] = lux value from sekonik")
        return
    if cmd=="setup":
        lux_min = _5600K_lx_range[0]
        lux_max = _5600K_lx_range[1]
        lux_range = lux_max - lux_min
        _5600Klx_points[0] = lux_min
        _5600Klx_points[1] = lux_min+lux_range/4
        _5600Klx_points[2] = lux_min+lux_range/2
        _5600Klx_points[3] = lux_min+lux_range/4*3
        _5600Klx_points[4] = lux_max
    
def update5600(intensity, offset=(0,0,0,0) ):
    print("lux range: "+str(int(_5600Klx_points[intensity]*0.95))+" - "+str(int(_5600Klx_points[intensity]*1.05)))
        
    

        

