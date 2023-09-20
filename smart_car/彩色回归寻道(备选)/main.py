
THRESHOLD = (40, 64, -6, 15, -23, 7) # 赛道颜色LAB，当前测试色灰
#THRESHOLD = (39, 60, 6, 22, -15, 1)

import sensor, image, time
#from pyb import LED
#import car
from pid import PID
rho_pid = PID(p=0.4, i=0) # 中竖线线左右偏移量
theta_pid = PID(p=0.001, i=0) # 中竖线线斜率

sensor.reset()
#sensor.set_vflip(True) # 垂直翻转
#sensor.set_hmirror(True) # 水平翻转
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.set_auto_exposure(False, 60000)
sensor.set_auto_gain(False) # 关闭自动自动增益
sensor.set_auto_whitebal(False, rgb_gain_db = (62.1991, 60.2071, 62.4124)) # 手动白平衡增益值（测试房间的值）要根据实际更改
sensor.skip_frames(time = 2000)
clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot().binary([THRESHOLD]) # 获取图像帧并将赛道颜色THRESHOLD和其余颜色分割
    img.erode(1) # 分割边缘删除像素
    line = img.get_regression([(100,100)], robust = True) # 获取线条
    if (line):
        rho_err = abs(line.rho())-img.width()/2
        if line.theta()>90:
            theta_err = line.theta()-180
        else:
            theta_err = line.theta()
        img.draw_line(line.line(), color = 127) # 显示中竖线
        #print(rho_err,line.magnitude(),rho_err)
        if line.magnitude()>8:   # magnitude越大效果越好
            #if -40<b_err<40 and -30<t_err<30:
            rho_output = rho_pid.get_pid(rho_err,1)
            theta_output = theta_pid.get_pid(theta_err,1)
            output = rho_output+theta_output # 左右偏移量加斜率值
            if -1<output<1:
                print("Go straight") # 直行
            elif output>1:
                print("turn right") # 车身往左偏，需往右调整
            elif output<-1:
                print("turn left") # 车身往右偏，需往左调整
        else:                    # 回归效果差，停止前进
            print("stop")
    else:                        # 没有检测到跑道
        print("find runway")
        pass
    #print(clock.fps())
