import cv2
import mediapipe as mp


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5, minLegalLm=15, debug=False):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.minLegalLm = minLegalLm

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode,
                                        max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

        self.isCal = False
        self.debug = debug
        self.x_center = 0
        self.y_center = 0

    def calDetectionZone(self, img):
        h, w, c = img.shape

        offset = 20
        zone_h, zone_w = h // 2, w // 2
        self.x_center, self.y_center = zone_w, zone_h

        self.start_point_x = self.x_center - zone_w // 2 - offset
        self.start_point_y = self.y_center - zone_h // 2 - offset
        self.end_point_x = self.x_center + zone_w // 2 + offset
        self.end_point_y = self.y_center + zone_h // 2 + offset
        # print(zone_h, zone_w)
        self.isCal = True
        return

    def detectionZone(self, img):
        if not self.isCal:
            self.calDetectionZone(img)

        start_point = (self.start_point_x, self.start_point_y)
        end_point = (self.end_point_x, self.end_point_y)
        color = (0, 0, 255)
        thickness = 2

        img = cv2.rectangle(img, start_point, end_point, color, thickness)
        return img

    def findHands(self, img):
        img = self.detectionZone(img)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if self.debug:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def preProcess(self, img, landmarks):
        h_array = []
        w_array = []
        for lm in landmarks:
            h_array.append(lm[2])
            w_array.append(lm[1])

        # CENTER
        lm_x_center = (max(w_array) + min(w_array)) // 2
        lm_y_center = (max(h_array) + min(h_array)) // 2

        # if self.debug:
        #     cv2.circle(img, (lm_x_center, lm_y_center), 10, (255, 0, 255), cv2.FILLED)

        vector_to_center = [self.x_center - lm_x_center, self.y_center - lm_y_center]

        lm_temp = landmarks

        # center position
        for i in range(len(landmarks)):
            lm_temp[i][1] = landmarks[i][1] + vector_to_center[0]
            lm_temp[i][2] = landmarks[i][2] + vector_to_center[1]
        # vector AA' = vector tinhtien
        # x_A' - xA = x_tt
        # => x_A' = x_tt + x_A

        # RESIZE
        height = self.end_point_y - self.start_point_y - 25
        # width = self.end_point_x - self.start_point_x
        size_h = max(h_array) - min(h_array)
        # size_w = max(w_array) - min(w_array)
        coefficient = height / size_h
        # print(coefficient)

        for i in range(len(lm_temp)):
            lm_temp[i][1] = round(coefficient * lm_temp[i][1] + (1 - coefficient) * self.x_center)
            lm_temp[i][2] = round(coefficient * lm_temp[i][2] + (1 - coefficient) * self.y_center)
            if self.debug:
                cv2.circle(img, (lm_temp[i][1], lm_temp[i][2]), 7, (51, 140, 232), cv2.FILLED)
        return lm_temp

    def findPosition(self, img, handNo=0):
        if not self.isCal: self.calDetectionZone(img)

        legal_lm = 0
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                if (self.start_point_x < cx < self.end_point_x and
                        self.start_point_y < cy < self.end_point_y):
                    legal_lm += 1
                    lmList.append([id, cx, cy])

        if legal_lm < self.minLegalLm:
            return []
        # print(legal_lm)
        return self.preProcess(img, lmList)
