
import numpy as np

from PIL import Image, ImageDraw


class Mask:
    def __init__(self, target_contour, target_id):
        self.target_id = target_id
        self.mask = self.__create_mask(target_contour)

    def collides_with(self, polygon):
        for p in polygon:
            if int(p[0]) > 1919 or int(p[1]) > 1079:
                continue

            if self.collides_with_point(p):
                return True

        return False

    def collides_with_point(self, p):
        if int(p[0]) > 1919 or int(p[0]) < 0 or int(p[1]) > 1079 or int(p[1]) < 0:
            return False

        if self.mask[int(p[1])][int(p[0])] == 1:
            return True

        return False

    def __create_mask(self, contour):
        img = Image.new('L', (1920, 1080), 0)
        ImageDraw.Draw(img).polygon(contour, 1, 1)

        return np.array(img)
