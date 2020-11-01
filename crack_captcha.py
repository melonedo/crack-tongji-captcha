import requests
from find_chars import read_base64, isolate_chars
from match_samples import load_samples, match_best


sample_set = load_samples("samples")

def crack(image):
    chars = isolate_chars(image)
    code = ""
    for char in chars:
        best = match_best(char, sample_set)
        code += best.char
    return code

if __name__ == "__main__":
    url = "https://ids.tongji.edu.cn:8443/nidp/app/login?sid=0,0&flag=true"
    import requests
    import cv2
    image = read_base64(requests.get(url).text)
    cv2.imshow("Captcha image", image)
    code = crack(image)
    print(code)
    cv2.waitKey()
