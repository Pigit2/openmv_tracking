# Untitled - By: huang - 周四 7月 27 2023

import sensor, image, time, pyb
from pyb import UART


uart = UART(1, 115200) # 使用串口1
#uart.init(115200, bits=8, parity=None, stop=1)


#GREY_Thresholds = [(14, 57, -2, 21, -24, 4)]  # 灰
GREY_Thresholds = [(17, 65, 0, 28, -33, 2)]
#RED_Thresholds  = [(12, 71, 18, 52, -8, 40)]  # 深红
RED_Thresholds  = [(1, 42, 14, 63, 6, 53)]  # 深红
YG_Thresholds   = [(17, 65, 0, 28, -33, 2),
                   (64, 99, -23, 34, 15, 46)]   # 灰+黄


ROIS1 = [# 左上x 左上y   宽  高  权
            (0, 180,   320, 60, 0), #下1
            (0, 60,   320, 120, 0), #中2
            (0,  0,    320, 60, 0)  #上3
        ]


#---------------------------------------摄像头初始化-----------------------------------------#

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)                   # 320*240/160*120
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)                         # 颜色追踪关闭自动增益
sensor.set_auto_whitebal(False)                     # 颜色追踪关闭白平衡

i=0  #第几行数据
j=0

discharge_flag = 0
mode_flag = 0  # 模式标志
#cross_num = 0 #第几个路口
#back_flag = 0  #返回的标志

#区域标志
center_flag1 = 0
center_flag2 = 0
center_flag3 = 0
center_flag4 = 0
center_flag5 = 0

#x位置标志
#bottom_x = 0
#middle_x = 0


out_str1=''  #打印字符串
clock = time.clock()


#--------------------------------------while循环开始-----------------------------------------#

while(True):
    clock.tick()
    img=sensor.snapshot()
    img.lens_corr(1.5) # 鱼眼矫正

    #--------------------------------------PART1：出发--------------------------------------#
    if(mode_flag==0): # 第一部分
        for r in ROIS1:
           i=i+1;
           blobs=img.find_blobs(GREY_Thresholds, roi=r[0:4], merge=True,pixels_area=10) # r[0:4] is roi tuple.
           if blobs:#如果找到了颜色块
                # 寻找最大色块
                largest_blob = max(blobs, key=lambda b: b.pixels())
                if(i==1):#下面矩形
                    if(largest_blob[2]>=20):#过滤20x20以下色块
                        if(largest_blob[3]>=20):
                            center_flag1=1;#下面的矩形找到的标志
                            img.draw_rectangle(largest_blob.rect()) #矩形框
                            img.draw_cross(largest_blob.cx(),largest_blob.cy()) #中心点
                            bottom_x = largest_blob.cx()  # 提取x坐标值

                elif(i==2):#中间矩形
                    if(largest_blob[2]>=20):
                        if(largest_blob[3]>=20):
                            center_flag2=1;
                            img.draw_rectangle(largest_blob.rect())
                            img.draw_cross(largest_blob.cx(),largest_blob.cy())
                            middle_x = largest_blob.cx()

                elif(i==3):#上面矩形
                    if(largest_blob[2]>=20):
                        if(largest_blob[3]>=20):
                            center_flag3=1;
                            img.draw_rectangle(largest_blob.rect())
                            img.draw_cross(largest_blob.cx(),largest_blob.cy())


        if(center_flag1 and center_flag2 and center_flag3): # 下中上识别到灰
            if(162 < bottom_x):               # 车身偏左，向右调整
                print("Right",bottom_x-160)
#                uart.write(str(bottom_x-160)+'\r'+'\n')

            elif(bottom_x < 158):             # 车身偏右，向左调整
                print("Left",bottom_x-160)
#                uart.write(str(bottom_x-160)+'\r'+'\n')

            elif(158 <= bottom_x <= 162):     # 下矩形居中，进中矩形再次判断车身
                if(162 < middle_x):           # 车身偏左，向右调整
                    print("Right",middle_x-160)
#                    uart.write(str(middle_x-160)+'\r'+'\n')
                elif(middle_x < 158):         # 车身偏右，向左调整
                    print("Left",middle_x-160)
#                    uart.write(str(middle_x-160)+'\r'+'\n')
                elif(158 <= middle_x <= 162): # 中下矩形均不偏，直行，左右容错两点像素
                    print("Keep Straight",middle_x-160)
#                    uart.write(str(middle_x-160)+'\r'+'\n')

        elif(center_flag1 and not center_flag2 and not center_flag3): # 仅下检测到灰色快，道路尽头
            print("Stop, SCAN")
            for code in img.find_qrcodes():
                print(code)
                mode_flag = 1   # 可使用超声波检测后再切换mode=1
                center_flag1 = 0
#                    uart.write(code.payload()+'\r'+'\n')



    #--------------------------------------PART2：出货--------------------------------------#
    if(mode_flag==1): # 第二部分
        for r in ROIS1:
           i=i+1;
           blobs=img.find_blobs(RED_Thresholds, roi=r[0:4], merge=True,pixels_area=10) # r[0:4] is roi tuple.
           if blobs:#如果找到了颜色块
                # 寻找最大色块
                largest_blob = max(blobs, key=lambda b: b.pixels())
                if(i==1):#下面矩形
                    if(largest_blob[2]>=20):#过滤20x20以下色块
                        if(largest_blob[3]>=20):
                            center_flag1=1;#下面的矩形找到的标志
                            img.draw_rectangle(largest_blob.rect()) #矩形框
                            img.draw_cross(largest_blob.cx(),largest_blob.cy()) #中心点
#                            bottom_x = largest_blob.cx()  # 提取x坐标值

                elif(i==2):#中间矩形
                    if(largest_blob[2]>=20):
                        if(largest_blob[3]>=20):
                            center_flag2=1;
                            img.draw_rectangle(largest_blob.rect())
                            img.draw_cross(largest_blob.cx(),largest_blob.cy())
#                            middle_x = largest_blob.cx()

                elif(i==3):#上面矩形
                    if(largest_blob[2]>=20):
                        if(largest_blob[3]>=20):
                            center_flag3=1;
                            img.draw_rectangle(largest_blob.rect())
                            img.draw_cross(largest_blob.cx(),largest_blob.cy())

        if(center_flag1):
            if(discharge_flag==0):
                j=j+1
                print("Stop, OPEN1:"+str(j))
                if(j>100):
                    discharge_flag = 1
                    j=0
                #discharge_flag = 1   #待主控返回完成卸货指令并移动一段时间后再执行
            elif(discharge_flag==1):
                j=j+1
                print("Stop, OPEN2:"+str(j))
                if(j>100):
                    mode_flag = 2


    #--------------------------------------PART3：返程--------------------------------------#
    if(mode_flag==2): # 第三部分
        for r in ROIS1:
           i=i+1;
           blobs=img.find_blobs(YG_Thresholds, roi=r[0:4], merge=True,pixels_area=10) # r[0:4] is roi tuple.
           if blobs:#如果找到了颜色块
                # 寻找最大色块
                largest_blob = max(blobs, key=lambda b: b.pixels())
                if(i==1):#下面矩形
                    if(largest_blob[2]>=20):#过滤20x20以下色块
                        if(largest_blob[3]>=20):
                            center_flag1=1;#下面的矩形找到的标志
                            img.draw_rectangle(largest_blob.rect()) #矩形框
                            img.draw_cross(largest_blob.cx(),largest_blob.cy()) #中心点
                            bottom_x = largest_blob.cx()  # 提取x坐标值

                elif(i==2):#中间矩形
                    if(largest_blob[2]>=20):
                        if(largest_blob[3]>=20):
                            center_flag2=1;
                            img.draw_rectangle(largest_blob.rect())
                            img.draw_cross(largest_blob.cx(),largest_blob.cy())
                            middle_x = largest_blob.cx()

                elif(i==3):#上面矩形
                    if(largest_blob[2]>=20):
                        if(largest_blob[3]>=20):
                            center_flag3=1;
                            img.draw_rectangle(largest_blob.rect())
                            img.draw_cross(largest_blob.cx(),largest_blob.cy())

        if(center_flag1 and center_flag2 and center_flag3): # 下中上识别到灰
            if(162 < bottom_x):               # 车身偏左，向右调整
                print("Right",bottom_x-160)
#                uart.write(str(bottom_x-160)+'\r'+'\n')

            elif(bottom_x < 158):             # 车身偏右，向左调整
                print("Left",bottom_x-160)
#                uart.write(str(bottom_x-160)+'\r'+'\n')

            elif(158 <= bottom_x <= 162):     # 下矩形居中，进中矩形再次判断车身
                if(162 < middle_x):           # 车身偏左，向右调整
                    print("Right",middle_x-160)
#                    uart.write(str(middle_x-160)+'\r'+'\n')
                elif(middle_x < 158):         # 车身偏右，向左调整
                    print("Left",middle_x-160)
#                    uart.write(str(middle_x-160)+'\r'+'\n')
                elif(158 <= middle_x <= 162): # 中下矩形均不偏，直行，左右容错两点像素
                    print("Keep Straight",middle_x-160)
#                    uart.write(str(middle_x-160)+'\r'+'\n')

        elif(center_flag1 and not center_flag2 and not center_flag3): # 仅下检测到灰色快，道路尽头
            print("Stop, END")
            mode_flag = 3




#        if(center_flag3 and not center_flag2 and center_flag1): # 上识别到红，只用上调整
#            if(162 < top_x):               # 车身偏左，向右调整
#                print("Right",top_x-160)
#        #                uart.write(str(bottom_x-160)+'\r'+'\n')
#            elif(top_x < 158):             # 车身偏右，向左调整
#                print("Left",top_x-160)
#        #                uart.write(str(bottom_x-160)+'\r'+'\n')
#            elif(158 <= top_x <= 162):     # 下矩形居中，进中矩形再次判断车身
#                print("Keep Straight",top_x-160)
#        #                    uart.write(str(middle_x-160)+'\r'+'\n')

#        elif(center_flag3 and center_flag2 and center_flag1): # 上中识别到红，使用上中调整
#            if(162 < top_x):               # 车身偏左，向右调整
#                print("Right",top_x-160)
#        #                uart.write(str(bottom_x-160)+'\r'+'\n')
#            elif(top_x < 158):             # 车身偏右，向左调整
#                print("Left",top_x-160)
#        #                uart.write(str(bottom_x-160)+'\r'+'\n')
#            elif(158 <= top_x <= 162):     # 下矩形居中，进中矩形再次判断车身
#                if(162 < middle_x):           # 车身偏左，向右调整
#                    print("Right",middle_x-160)
#        #                    uart.write(str(middle_x-160)+'\r'+'\n')
#                elif(middle_x < 158):         # 车身偏右，向左调整
#                    print("Left",middle_x-160)
#        #                    uart.write(str(middle_x-160)+'\r'+'\n')
#                elif(158 <= middle_x <= 162): # 中下矩形均不偏，直行，左右容错两点像素
#                    print("Keep Straight",middle_x-160)
#        #                    uart.write(str(middle_x-160)+'\r'+'\n')

#        elif(center_flag3 and center_flag2 and center_flag1): # 上中无
#            if(162 < bottom_x):               # 车身偏左，向右调整
#                print("Right",bottom_x-160)
#        #                uart.write(str(bottom_x-160)+'\r'+'\n')
#            elif(top_x < 158):             # 车身偏右，向左调整
#                print("Left",bottom_x-160)
#        #                uart.write(str(bottom_x-160)+'\r'+'\n')
#            elif(158 <= bottom_x <= 162):     # 下矩形居中，进中矩形再次判断车身
#                print("Keep Straight",bottom_x-160)
#        #                    uart.write(str(middle_x-160)+'\r'+'\n')

#        elif(not center_flag1 and not center_flag2 and not center_flag3): # 仅下检测到灰色快，道路尽头
#            print("Stop, OPEN DOOR")
#        #                    uart.write(code.payload()+'\r'+'\n')





    #--------------------------------------寻找棕色块的位置--------------------------------------#
#    for r in ROIS2:
#        j=j+1;
#        blobs=img.find_blobs(Above_Thresholds, roi=r[0:4], merge=True,pixels_area=10) # r[0:4] is roi tuple.
#        if blobs:#如果找到了颜色块
#            # 寻找最大色块
#            largest_blob = max(blobs, key=lambda b: b.pixels())
#            if(j==1):#左边的矩形找到了
#                if(largest_blob[2]>=20):
#                    if(largest_blob[3]>=20):
#                        center_flag3=1;
#                        img.draw_rectangle(largest_blob.rect())
#                        img.draw_cross(largest_blob.cx(),largest_blob.cy(),2)



#        #--------------------------------------执行命令-------------------------------------------#
#        if(center_flag3 and center_flag2 and center_flag1): # 上中下均检测到灰色快，直行道路
#            # x=160，y=240为中点，
#            if(162 < bottom_x):               # 车身偏左，向右调整
#                print("Right",bottom_x-160)
#                uart.write(str(bottom_x-160)+'\r'+'\n')

#            elif(bottom_x < 158):             # 车身偏右，向左调整
#                print("Left",bottom_x-160)
#                uart.write(str(bottom_x-160)+'\r'+'\n')

#            elif(158 <= bottom_x <= 162):     # 下矩形居中，进中矩形再次判断车身
#                if(162 < middle_x):           # 车身偏左，向右调整
#                    print("Right",middle_x-160)
#                    uart.write(str(middle_x-160)+'\r'+'\n')
#                elif(middle_x < 158):         # 车身偏右，向左调整
#                    print("Left",middle_x-160)
#                    uart.write(str(middle_x-160)+'\r'+'\n')
#                elif(158 <= middle_x <= 162): # 中下矩形均不偏，直行，左右容错两点像素
#                    print("Keep Straight",middle_x-160)
#                    uart.write(str(middle_x-160)+'\r'+'\n')

#        elif(not center_flag3 and center_flag2 and center_flag1): # 仅中下检测到灰色快，道路尽头
#            if(center_flag4):                 # 车库在左边
#                print("Turn Left")

#            elif(center_flag5):               # 车库在右边
#                print("Turn Right")

#            else:                             # 道路尽头扫描二维码
#                print("Road End")
#                for code in img.find_qrcodes():
#                    print(code)
#                    uart.write(code.payload()+'\r'+'\n')



    i=0
    #像素位移之和清零
    center_flag1 = 0 #区域标志
    center_flag2 = 0
    center_flag3 = 0
    center_flag4 = 0
    center_flag5 = 0

    #数组清零
    out_str1=''#清除之前的数据
