from HandDetectionModule import *
import csv
import os
import shutil
import time

# DATASET CLASS
Forward = 0
Back = 1
Left = 2
Right = 3
Forward_Left = 4
Forward_Right = 5
Back_Left = 6
Back_Right = 7
Stop = 8
Classes = [0, 1, 2, 3, 4, 5, 6, 7, 8]
ClassesName = ['Forward', 'Back', 'Left', ' Right', 'Forward_Left', 'Forward_Right', 'Back_Left', 'Back_Right', 'Stop']
number_of_each_dataset = 5000
# ____________________________

path = 'dataset.csv'
img_path = 'images'


def write_file(file_path, class_name, lm_list):
    if not os.path.exists(file_path):
        f = open(file_path, "w", newline='')

        temp_str = []
        for i in range(0, 22):  # 0 -> 21
            if i == 0:
                temp_str.append('class')
            else:
                temp_str.append('lm' + str(i - 1) + 'x')
                temp_str.append('lm' + str(i - 1) + 'y')
        
        writer = csv.writer(f)
        writer.writerow(temp_str)

        f.close()
    else:
        if not len(lm_list): return False
        f = open(file_path, 'a', newline='')

        temp_str = [class_name]
        count = 0
        print(lm_list)

        for i in range(21):
            # print(lm_list[count][0])
            if i == lm_list[count][0]:
                temp_str.append(str(lm_list[count][1]))
                temp_str.append(str(lm_list[count][2]))
                if count + 1 < len(lm_list):
                    count += 1
            else:
                temp_str.append('0')
                temp_str.append('0')
        writer = csv.writer(f)
        writer.writerow(temp_str)

        f.close()
    return True


def labeling():
    detector = handDetector(maxHands=1, debug=True)

    cap = cv2.VideoCapture(1)

    if not os.path.exists(img_path):
        os.mkdir(img_path)
    else:
        is_remove = input('Remove "img_path"?(Y/n): ')
        if is_remove == 'y' or is_remove == 'Y' or is_remove == 'yes' or is_remove == 'Yes':
            shutil.rmtree(img_path)
            os.mkdir(img_path)

    if os.path.exists(path):
        is_remove = input('Remove "dataset.csv"?(Y/n): ')
        if is_remove == 'y' or is_remove == 'Y' or is_remove == 'yes' or is_remove == 'Yes':
            os.remove(path)

    label_count = 0
    count = int(input('Staring label with: '))
    if count >= 9:
        print('error')
        return -1

    print('Label start!')
    save_path_dir = os.path.join(img_path, 'class_' + str(count))
    os.mkdir(save_path_dir)

    first_time_flag = False

    for i in range(5):
        print('count down:', 5 - i)
        time.sleep(1)

    while True:
        print('label:', label_count)
        if label_count == number_of_each_dataset:
            if count == 8:
                break
            print('Current label: ', Classes[count])
            print('Next label: ', Classes[count + 1])

            temp = input('Continue label?(Y/n): ')
            if not temp == 'y' or temp == 'Y' or temp == 'yes' or temp == 'Yes':
                return
            else:
                count += 1
                label_count = 0
                save_path_dir = os.path.join(img_path, 'class_' + str(count))
                os.mkdir(save_path_dir)

                for i in range(5):
                    print('count down:', 5 - i)
                    time.sleep(1)

        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)

        cv2.imshow("Image", cv2.flip(img, 1))
        if cv2.waitKey(1) == ord('q'):
            break

        if write_file(path, Classes[count], lmList) and first_time_flag:
            label_count += 1
            save_path = os.path.join(save_path_dir, 'frame' + str(label_count) + '.jpg')
            cv2.imwrite(save_path, cv2.flip(img, 1))

        first_time_flag = True


