import numpy
import cv2
import os
from os.path import join as join_path
import math
from collections import namedtuple


SampleImage = namedtuple("SampleImage", ["char", "image"])


class ShapeMismatch(Exception):
    "The shape of given images differ too much"
    pass


def get_samples(char, sfx):
    if char.isupper():
        char += 'c'
    for name in os.listdir(join_path(sfx, char)):
        yield join_path(sfx, char, name)


def load_samples(sfx):
    chars = filter(str.isalnum, map(chr, range(128)))
    samples = []
    for char in chars:
        samples += [SampleImage(char, cv2.imread(path, cv2.IMREAD_GRAYSCALE))
                    for path in get_samples(char, sfx)]
    return samples


def get_views(dst: numpy.ndarray, src: numpy.ndarray, tol=2):
    def get_starts(l, r):
        if abs(r-l) > tol:
            raise ShapeMismatch()
        return (l-r, 0) if l > r else (0, r-l)
    w_dst, w_src = get_starts(dst.shape[0], src.shape[0])
    h_dst, h_src = get_starts(dst.shape[1], src.shape[1])
    return dst[w_dst:, h_dst:], src[w_src:, h_src:]


def compare_image(l: numpy.ndarray, r: numpy.ndarray):
    try:
        views = get_views(l, r)
    except ShapeMismatch:
        return math.inf
    return cv2.norm(*views, cv2.NORM_L1)


def match_best(image, sample_set):
    return min(sample_set, key=lambda s: compare_image(image, s.image))


if __name__ == "__main__":
    import requests
    from find_chars import read_base64, isolate_chars
    url = "https://ids.tongji.edu.cn:8443/nidp/app/login?sid=0,0&flag=true"
    test_image = read_base64(requests.get(url).text)
    test_char = isolate_chars(test_image)[0]
    cv2.imshow("test", test_char)
    sample_set = load_samples("samples/")
    best = match_best(test_char, sample_set)
    cv2.imshow("best", best.image)
    print(best.char, compare_image(best.image, test_char))
    cv2.waitKey()
