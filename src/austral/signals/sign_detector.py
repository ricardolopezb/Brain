import cv2 as cv


class SignDetector:
    def __init__(self):
        self.sift = cv.SIFT_create()
        self.check_existing_files()
        self.base_signal_images = {
            'crosswalk': self._generate_keypoints_and_descriptors(cv.imread('src/austral/signals/signs/crosswalk.png', cv.IMREAD_GRAYSCALE)),
            'parking': self._generate_keypoints_and_descriptors(cv.imread('src/austral/signals/signs/parking.png', cv.IMREAD_GRAYSCALE)),
            'stop': self._generate_keypoints_and_descriptors(cv.imread('src/austral/signals/signs/stop.png', cv.IMREAD_GRAYSCALE)),
            'yield': self._generate_keypoints_and_descriptors(cv.imread('src/austral/signals/signs/yield.png', cv.IMREAD_GRAYSCALE))
        }
        self.flann = self._setup_flann()

    def detect_signal(self, image):
        coincidence_percentage = {}
        print("TYPE OF IMAGE: ", type(image))
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
            coincidence_percentage.values()) > 0 else None


    def _generate_keypoints_and_descriptors(self, img):
        return self.sift.detectAndCompute(img, None)

    def _setup_flann(self):
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=12)
        search_params = dict(checks=200)  # or pass empty dictionary
        return cv.FlannBasedMatcher(index_params, search_params)

    def check_existing_files(self):
        import os
        if os.path.exists('src/austral/signals/signs/crosswalk.png'):
            print('The file crosswalk.png does exist')
        else:
            print('The file crosswalk.png does not exist')
        if os.path.exists('src/austral/signals/signs/parking.png'):
            print('The file parking.png does exist')
        else:
            print('The file parking.png does not exist')
        if os.path.exists('src/austral/signals/signs/stop.png'):
            print('The file stop.png does exist')
        else:
            print('The file stop.png does not exist')
        if os.path.exists('src/austral/signals/signs/yield.png'):
            print('The file yield.png does exist')
        else:
            print('The file yield.png does not exist')
