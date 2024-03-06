import cv2 as cv
import torch
import pathlib

class SignDetector:
    pathlib.WindowsPath = pathlib.PosixPath
    def __init__(self):
        self.sift = cv.SIFT_create()
        self.base_signal_images = {
            #'crosswalk': self._generate_keypoints_and_descriptors(cv.imread('src/austral/signals/signs/crosswalk.png', cv.IMREAD_GRAYSCALE)),
            #'parking': self._generate_keypoints_and_descriptors(cv.imread('src/austral/signals/signs/parking.png', cv.IMREAD_GRAYSCALE)),
            'stop': self._generate_keypoints_and_descriptors(cv.imread('src/austral/signals/signs/stop.png', cv.IMREAD_GRAYSCALE)),
            #'yield': self._generate_keypoints_and_descriptors(cv.imread('src/austral/signals/signs/yield.png', cv.IMREAD_GRAYSCALE))
        }
        self.flann = self._setup_flann()


    def detect_signal(self, image, threshold=0):
        coincidence_percentage = {}
        kp2, des2 = self.sift.detectAndCompute(image, None)

        for signal_name, (kp1, des1) in self.base_signal_images.items():
            matches = self.flann.knnMatch(des1, des2, k=2)

            good_matches = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)

            if len(kp1) + len(kp2) > 0:  # Evita la división por cero
                match_percentage = (len(good_matches) / ((len(kp1) + len(kp2)) / 2)) * 100
            else:
                match_percentage = 0
            coincidence_percentage[signal_name] = match_percentage

        # return the key of the one with the highest percentage. If it is zero, return None
        return max(coincidence_percentage, key=coincidence_percentage.get) if max(
            coincidence_percentage.values()) > threshold else None


    def _generate_keypoints_and_descriptors(self, img):
        return self.sift.detectAndCompute(img, None)

    def _setup_flann(self):
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=12)
        search_params = dict(checks=200)  # or pass empty dictionary
        return cv.FlannBasedMatcher(index_params, search_params)

