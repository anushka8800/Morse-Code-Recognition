morse_code_dict = {
    ".-": "a",
    "-...": "b",
    "-.-.": "c",
    "-..": "d",
    ".": "e",
    "..-.": "f",
    "--.": "g",
    "....": "h",
    "..": "i",
    ".---": "j",
    "-.-": "k",
    ".-..": "l",
    "--": "m",
    "-.": "n",
    "---": "o",
    ".--.": "p",
    "--.-": "q",
    ".-.": "r",
    "...": "s",
    "-": "t",
    "..-": "u",
    "...-": "v",
    ".--": "w",
    "-..-": "x",
    "-.--": "y",
    "--..": "z",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
    "-----": "0",
}

from flask import Flask, render_template, Response, request
import datetime

import cv2
import mediapipe as mp

app = Flask(__name__)


# initialize mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

def generate_frames():

    cap = cv2.VideoCapture(0)

    start_time = 0
    end_time = 0
    tapped = 0
    # timeDiff = 0
    upDiff = 0
    str1=""
    deleting = 0

    ret = True
    while ret:
        # Read each frame from the webcam
        ret, frame = cap.read()

        # Flip the frame vertically
        frame = cv2.flip(frame, 1)
        #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Get hand landmark prediction
        result = hands.process(framergb)

        # post process the result
        if result.multi_hand_landmarks:
            landmarks = []
            for handslms in result.multi_hand_landmarks:
                for lm in handslms.landmark:
                    
                    lmx = int(lm.x * 640)
                    lmy = int(lm.y * 480)

                    landmarks.append([lmx, lmy])
                mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)
                
            fore_finger = (landmarks[8][0],landmarks[8][1])
            thumb = (landmarks[4][0],landmarks[4][1])
            middle_finger = (landmarks[12][0],landmarks[12][1])
            
            diff=thumb[1]-fore_finger[1]
            diff2=thumb[1]-middle_finger[1]
            #print("diff: ",diff)
                
            if(tapped == 0):
                if (diff<40):
                    tapped = 1
                    if (start_time == 0):
                        start_time = datetime.datetime.now()
                        
                    if(start_time != 0 and end_time !=0):
                        upDiff = (start_time - end_time).total_seconds()
                        
                        #LETTER SPACES--------
                        if(upDiff>=1 and upDiff<=3):
                            str1+=" "
                           
                        
                        #WORD SPACE-----------
                        elif(upDiff>3 and upDiff<=8):
                            str1+="/"
                        end_time=0

                if(diff2<40):
                    if(len(str1) and deleting == 0):
                        deleting = 1
                        str1=""
                if (diff2>100): deleting = 0        
                            
                                
            if (tapped == 1):
                if(diff>100):
                    tapped = 0
                    
                    if (end_time == 0):
                        end_time = datetime.datetime.now()
                        tapDiff = (end_time - start_time).total_seconds()
                        
                        #DOTS-------
                        if(tapDiff>=0.1 and tapDiff<=1):
                            str1+="."
                            # cv2.putText(frame, ".", (600, 25), cv2.FONT_ITALIC, 4, (255,255,255), 2)

                                                    
                        #DASHES-------
                        elif(tapDiff>=1 and tapDiff<=3):
                            str1+="-"
                            # cv2.putText(frame, ".", (600, 25), cv2.FONT_ITALIC, 3, (255,255,255), 2)
                        start_time=0
                #print("The time diff is: ", timeDiff)

        l1=str1.split('/')
        output=""
        #print(l1)

        for i in l1:
            if(' ' in i):
                l2=i.split(' ')
                for j in l2:
                    try:
                        output+=morse_code_dict[j]
                    except KeyError:
                        pass
                        #print("Wrong input, try again!!!")
            else:
                try:
                    output+=morse_code_dict[i]
                except KeyError:
                    pass
                    #print("Wrong input, try again!!!")
            output+=" "

        # define the font and text properties
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        thickness = 2
        color = (255, 255, 255)

        # get the size of the text
        text_size = cv2.getTextSize(output, font, font_scale, thickness)[0]

        # calculate the position of the text in the frame
        text_x = int((frame.shape[1] - text_size[0]) / 2)
        text_y = int((frame.shape[0] + text_size[1]) / 1.1)

        # draw the text on the frame
        cv2.putText(frame, output, (text_x, text_y), font, font_scale, color, thickness)
        
        

       
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
    # print(str1)
    # print("Result: ",output)
    cap.release();
    cv2.destroyAllWindows()


# @app.route("/")
# def index():
#     return render_template('index.html')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/video")
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)
