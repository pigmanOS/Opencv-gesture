import cv2
import mediapipe as mp
import time
import serial

#基于opencv的手势识别系统，参考代码google的开源项目 https://github.com/googlesamples/mediapipe
#已上传github:https://github.com/pigmanOS/Opencv-gesture.git

cap = cv2.VideoCapture(0)

#使用预训练的手势模型
mpHands = mp.solutions.hands
hands = mpHands.Hands()

#绘制追踪线
mpDraw = mp.solutions.drawing_utils
handLmsStyle = mpDraw.DrawingSpec(color=(0, 0, 225), thickness=5)
handlConStyle = mpDraw.DrawingSpec(color=(0, 225, 0), thickness=5)

Ptime = 0
Ctime = 0

fingertip = [4, 8, 12, 16, 20]
#指尖的编号

values = {
            0 : b'0\r\n',
            1 : b'1\r\n',
            2 : b'2\r\n',
            3 : b'3\r\n',
            4 : b'4\r\n',
            5 : b'5\r\n',
}

ser = serial.Serial()#打开串口
ser.baudrate = 9600
ser.port = "COM5"
ser.open()


def find_positon(img,ret):
    lmslist = []
    if ret:
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换图片格式
        result = hands.process(imgRGB) # 返回手势识别数据
        # print(result.multi_hand_landmarks) # 21个点的坐标
        imgHeight = img.shape[0]  # 得到视窗高度和宽度
        imgWidth = img.shape[1]
        if result.multi_hand_landmarks:
            for handlms in result.multi_hand_landmarks:
                mpDraw.draw_landmarks(img, handlms, mpHands.HAND_CONNECTIONS, handLmsStyle, handlConStyle)#在这一帧绘制追踪线
                for i, lm in enumerate(handlms.landmark):
                    #lm是归一化平面坐标
                    xPos = int(lm.x * imgWidth)
                    yPos = int(lm.y * imgHeight)
                    lmslist.append([i, xPos, yPos])
                    # 记录每个点的坐标
        return lmslist



while True:
    ret, img = cap.read()
    lmslist = find_positon(img=img, ret=ret)
    if len(lmslist):
        fingers = []
        if lmslist[1][1] < lmslist[0][1]:
            for tid in fingertip:
                if tid == 4:  # 即大指拇,如果大拇指指尖X坐标大于大拇指第二个关节X坐标，即代表大拇指折叠
                    if lmslist[tid][1] > lmslist[tid - 1][1]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                else:         # 其他几个指头情况一样，如果指尖的Y坐标大于往下两个关节的Y坐标，即代表改关节弯曲
                    if lmslist[tid][2] > lmslist[tid - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
        elif lmslist[1][1] == lmslist[0][1]:
            for tid in fingertip:
                if tid == 4:  # 即大指拇,如果大拇指指尖X坐标大于大拇指第二个关节X坐标，即代表大拇指折叠
                    if lmslist[tid][2] < lmslist[tid - 1][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                else:         # 其他几个指头情况一样，如果指尖的Y坐标大于往下两个关节的Y坐标，即代表改关节弯曲
                    if lmslist[tid][1] < lmslist[tid - 2][1]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
        else:
            for tid in fingertip:
                if tid == 4:  # 即大指拇,如果大拇指指尖X坐标大于大拇指第二个关节X坐标，即代表大拇指折叠
                    if lmslist[tid][1] < lmslist[tid - 1][1]:
                        fingers.append(1)
                    else:
                        fingers.append(0)
                else:         # 其他几个指头情况一样，如果指尖的Y坐标大于往下两个关节的Y坐标，即代表改关节弯曲
                    if lmslist[tid][2] < lmslist[tid - 2][2]:
                        fingers.append(1)
                    else:
                        fingers.append(0)

        cnt = fingers.count(1)

        # 记录弯曲数量
        cv2.putText(img, str(cnt), (30, 150), cv2.FONT_HERSHEY_PLAIN, 5, (30, 60, 90), 3)

        ser.write(values.get(cnt))

        Ctime = time.time()#计算帧率
        fps = 1/(Ctime-Ptime)
        Ptime = Ctime
        cv2.putText(img, f"FPS : {int(fps)}", (30, 50), cv2.FONT_HERSHEY_PLAIN, 2, (50, 160, 0), 3)


    cv2.imshow('img', img)
    if cv2.waitKey(1) == ord('q'):
         break


ser.close()
cap.release()
cv2.destroyAllWindows()
