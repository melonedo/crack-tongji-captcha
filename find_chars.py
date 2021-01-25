from PIL import Image
from io import BytesIO
from base64 import b64decode
import numpy
import re
import cv2
import random
from collections import namedtuple
from math import hypot


if cv2.__version__.split()[0] == '3':
    old_find_contours = cv2.findContours

    def new_find_contours(*args, **kwargs):
        return old_find_contours(*args, **kwargs)[1:]
    cv2.findContours = new_find_contours


class CharacterTooComplicated(Exception):
    pass


RotatedRect = namedtuple("RotatedRect", "center, size, angle")


DEFAULT_SIZE = (40, 50)


def read_base64(data_url):
    "Read and binarize an image from data_url."
    image_str = re.fullmatch("data:image/jpg;base64,(.+)", data_url).group(1)
    pil_image = Image.open(BytesIO(b64decode(image_str)))
    raw_image = ~cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2GRAY)
    _, binary_image = cv2.threshold(raw_image, 10, 255, cv2.THRESH_BINARY)
    return binary_image


def draw_rotated_rect(image, rrect):
    box = cv2.boxPoints(rrect)
    for i in range(4):
        cv2.line(image, tuple(box[i]), tuple(box[(i+1) % 4]), 250, 1)


def get_angle(rrect):
    "Get the nearest angle to make the rectangle up-right."
    return rrect.angle if rrect.angle < 45 else -90 + rrect.angle

def findContours(image):
    "Work around the difference between opencv 3 and opencv 4."
    return cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]

def find_chars(image):
    "Find the characters in image, return them as rotated rectangles."
    contours = findContours(image)
    # print(contours)
    rrects = [RotatedRect(*cv2.minAreaRect(c)) for c in contours]
    if len(contours) != 4:  # i and j
        if len(contours) < 4:  # some lost character
            raise CharacterTooComplicated()

        def get_area(rrect):
            return rrect.size[0]*rrect.size[1]
        dot_indices = filter(
            lambda i: get_area(rrects[i]) < 40, range(len(rrects)))
        body_indices = list(filter(
            lambda i: get_area(rrects[i]) >= 40, range(len(rrects))))
        if len(body_indices) != 4:
            raise CharacterTooComplicated()
        for di in dot_indices:
            def get_distance(i):
                return hypot(
                    rrects[di].center[0] - rrects[i].center[0],
                    rrects[di].center[1] - rrects[i].center[1])
            nearest = min(body_indices, key=get_distance)
            # print(nearest)
            joined_contour = numpy.concatenate(
                (contours[di], contours[nearest]))
            rrects[nearest] = RotatedRect(*cv2.minAreaRect(joined_contour))
        rrects = [rrects[i] for i in body_indices]
    return rrects


def crop_rrect(image, rrect, margin):
    "Crop a rotated rectangle from image."
    mat = cv2.getRotationMatrix2D(rrect.center, get_angle(rrect), 1)
    size = int(rrect.size[0]+margin*2), int(rrect.size[1]+margin*2)
    if get_angle(rrect) <= 0:
        size = size[1], size[0]
    for i in (0, 1):
        mat[i, 2] += size[i] / 2 - rrect.center[i]

    dst = cv2.warpAffine(image, mat, size, cv2.INTER_LINEAR)
    # print(get_angle(rrect), size, rrect)
    return dst


def isolate_chars(image, margin=0):
    "Find the characters in the image, return them as images."
    rrects = sorted(find_chars(image), key=lambda rrect: rrect.center)
    cropped = [crop_rrect(image, rrect, margin) for rrect in rrects]
    return cropped


def concat_chars(chars, size=DEFAULT_SIZE):
    "Concatenate the characters to form a whole picture for use in tesseract."
    canvas = numpy.zeros((size[1], size[0]*4), numpy.uint8)
    for i in range(4):
        char_size = chars[i].shape
        high = (size[1]+char_size[0])//2, (size[0]+char_size[1])//2
        low = high[0]-char_size[0], high[1]-char_size[1]
        canvas[
            low[0]: high[0],
            size[0]*i + low[1]: size[0]*i + high[1],
        ] = chars[i]
    return canvas


if __name__ == "__main__":
    image_url = "data:image/jpg;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAABFCAIAAACAFD7PAAACKUlEQVR42u3bwU3EMBBG4ZRDF9sHlVABEjTCgTqohTICp2iVaLP22DP/2HlPuREJKfmYxN5lWYkcWrgEBCwCFgGLCFgELAIWEbBS9/L+w0UAVmdS28HVAFZnUsACliMsbAGLoQUshhawsAUsYmhJYX1/vm7HBdFgKwJWCa85CFYRAZY7rOPJwzmzEcGWI6wJVJmJAMsL1hyqsJUL1kyqWogAqyesyVQxtFLDmmlVyNASwBKq+vh6Y2jNCUs7q/5hbUfyrQftzf693XZHaljyJ+A9LCdeow+tIylvXnZYeV7YA2ANPbTOVTnxaoKVZBmogmUbWjlVdbe12FSdwIr/iyyE1c6ui620qrLAyrNrVQKry1QbC9ZTOq62LgHreEKkrTywIteJ/WElfMfqpcoAS/iOVYgGWEZYHVXV2hJuN5SPopFg5dlu6K6qXIx2E6v2GZcO1vneqRaWk6pHaJ4e2vVg8GOkCVbhT4NheY8rmy359tUwsGpPCIblqqrWVvxKeWZYkd9u2OkJUFVua1U0Dyzh0CqB5ffbs5G6BKwYW4/2PwNUpa12dzQ1LJUtYNlsZfys0LZ4lMBar5rwE+hSWO3/qqqCtV67qWDFv8Wjqt2W7B1r56YWlqstYDXaUq4KbQlh4amEl367IXOoStiCKgIWmwvAUqgCFrAYV8AaBBb3ElhsLgArtzDuH7AIWETAImARsIiARcAiYBEBi4BFwCICFgGLgEVk6g+FZO0jKAvv3AAAAABJRU5ErkJggg=="
    image = read_base64(image_url)
    cv2.imshow("src", image)
    chars = isolate_chars(image)
    for i in range(4):
        cv2.imshow(f"character {i}", chars[i])
    concat = concat_chars(chars)
    cv2.imshow("concat", concat)
    # cv2.imwrite("c.png", ~concat)
    cv2.waitKey()
