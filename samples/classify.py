from os import rename

def read():
    num, char = input().split()
    if char.isupper():
        char = char + 'c'
    rename(num+".png", f"{char}/{num}.png")

while True:
    read()