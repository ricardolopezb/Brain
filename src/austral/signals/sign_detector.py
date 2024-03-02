import cv2 as cv


class SignDetector:
    def __init__(self):
        self.sift = cv.SIFT_create()
        self.base_signal_images = {}
        self.flann = self._setup_flann()
        for signal_name, path in self.image_paths.items():
            img = cv.imread(path, cv.IMREAD_GRAYSCALE)
            if img is None:
                print(f"Failed to load image at path: {path}")
            self.base_signal_images[signal_name] = self._generate_keypoints_and_descriptors(img)

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
