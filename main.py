import cv2
import time
import random
from sklearn import svm
from CreateDataset import *
from HandDetectionModule import *
from ReadCSV import *
from paho.mqtt import client as mqtt_client


# class define
ClassesName = ['Forward', 'Back', 'Left', 'Right', 'Forward_Left', 'Forward_Right', 'Back_Left', 'Back_Right', 'Stop']
Signal = ['F', 'B', 'L', 'R', 'G', 'I', 'H', 'J', 'S']

# mqtt define
broker = 'broker.emqx.io'
port = 1883
topic = "/Team10/car_controller"
client_id = f'python-mqtt-{random.randint(0, 1000)}'


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, message):
    msg = f"messages: {message}"
    result = client.publish(topic, message)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{message}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def main():
    print('Data processing!!!')
    y_train, x_train = dataset_reader(pd.read_csv('dataset.csv', sep=','))
    clf = svm.SVC()
    clf.fit(x_train, y_train)
    print('Done!!!')

    client = connect_mqtt()
    client.loop_start()

    detector = handDetector(maxHands=1, debug=True)
    cap = cv2.VideoCapture(1)
    car_cam = cv2.VideoCapture('http://192.168.0.116:81/stream')

    first_flag = True
    pre_predict = None

    while True:
        success, img = cap.read()
        success_car, img_car = car_cam.read()

        if success and success_car:
            img = detector.findHands(img)
            h, w, c = img.shape
            # # cv2.circle(img, (w // 2, h // 2), 15, (255, 0, 255), cv2.FILLED)
            lmList = detector.findPosition(img)
            if lmList != [] and first_flag:
                first_flag = False
                continue
            cv2.imshow("Image", cv2.flip(img, 1))
            cv2.imshow("Car", cv2.rotate(img_car, cv2.cv2.ROTATE_90_CLOCKWISE))
            #
            # print('step')

            if len(lmList) != 0:
                lm_list = preprocess_lm_list(lmList)
                # print(lm_list)
                temp = clf.predict([lm_list])[0]
                if temp != pre_predict:
                    print('predict:', ClassesName[temp])
                    publish(client, Signal[temp])
                    pre_predict = temp
            if cv2.waitKey(1) == ord('q'):
                break
    # labeling()


if __name__ == '__main__':
    main()
