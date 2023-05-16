import time

import numpy as np
import random
import os
from picamera2 import Picamera2, Preview
from libcamera import Transform
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
from touch_input import TouchInput
from settings_screen import SettingsScreen
import json

screen_width = 480
screen_height = 800
font_path = "comic_sans.ttf"

def load_settings():
    try:
        with open('settings.json') as f:
            return json.load(f)
    except:
        print("Could not read settings.json. Returning defaults")
        return {"contrast": 1.4, "brightness": 1.2}

def save_settings():
    try:
        with open('settings.json', "w") as f:
            f.write(json.dumps({"contrast": settings_screen.contrast, "brightness": settings_screen.brightness}))
    except:
        print("Could not write settings.json")

img_counter=1
def save_image_to_disk(source):
    global img_counter
    try: 
        output = json.loads(os.popen('lsblk -Jp').read())
        for device in output["blockdevices"]:
            if device["name"].startswith('/dev/sd'):
                for partition in device["children"]:
                    mountpoint = "/mnt/usbstick"
                    if not partition["mountpoint"]:
                        print("Trying to mount USB Storage")
                        os.system("sudo mkdir -p {}".format(mountpoint))
                        os.system("sudo mount {} {}".format(partition["name"], mountpoint))
                    else: 
                        mountpoint = partition["mountpoint"]
                    dest = mountpoint + "/photobooth_{}.jpg".format(img_counter)
                    while os.path.exists(dest):
                        img_counter += 1
                        dest = mountpoint + "/photobooth_{}.jpg".format(img_counter)
                    os.system("sudo cp {} {}".format(source, dest))
    except Exception as e: 
        print("failed to save image to USB stick")
        print(e)

def countdown_text(text, size = 350):
    txt = Image.new("RGBA", (screen_width, screen_height), (0, 0, 0, 0))
    fnt = ImageFont.truetype(font_path, size)
    (left, top, right, bottom) = fnt.getbbox(text)
    text_height = bottom-top
    text_width = right-left
    d = ImageDraw.Draw(txt)
    draw_cam_overlay(d)
    d.text((screen_width/2-text_width/2, (screen_height/2)-(text_height/2)-top), text, font=fnt, fill=(255, 153, 255, 190))
    return np.rot90(np.asarray(txt), -1)

def cam_overlay():
    im = Image.new("RGBA", (screen_width, screen_height), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    draw_cam_overlay(d)
    return np.rot90(np.asarray(im), -1)

screen_overlay_bar_height = 160
screen_overlay_outer_pad = 20
trigger_x1 = (screen_width/2)-(screen_overlay_bar_height/2) + screen_overlay_outer_pad
trigger_y1 =  screen_height-screen_overlay_bar_height + screen_overlay_outer_pad
trigger_x2 = (screen_width/2)+(screen_overlay_bar_height/2) - screen_overlay_outer_pad
trigger_y2 = screen_height - screen_overlay_outer_pad

def draw_cam_overlay(d):
    d.rectangle((0, screen_height-screen_overlay_bar_height, screen_width, screen_height), fill=(0, 0, 0, 255))
    d.ellipse(
        (trigger_x1, trigger_y1, trigger_x2, trigger_y2), 
        fill = (0xed, 0xed, 0xed, 255), 
        width=0
    )
    pad = 7
    d.ellipse(
        (trigger_x1 + pad, trigger_y1 + pad, trigger_x2 - pad, trigger_y2 - pad), 
        fill = (0xed, 0xed, 0xed, 255), 
        outline =(0xcc, 0xcc, 0xcc, 255), 
        width=7
    )

def process_image(image_path):
    im = ImageOps.mirror(Image.open(image_path).rotate(-90,expand=True))
    im = im.crop((0, 0, screen_width, screen_height-screen_overlay_bar_height))
    im.save('original_img.jpg')
    contrast = ImageEnhance.Contrast(im)
    im = contrast.enhance(settings_screen.contrast)
    brightness = ImageEnhance.Brightness(im)
    im = brightness.enhance(settings_screen.brightness)
    im.save('processed_img.jpg')
    os.system('lp -d EPS processed_img.jpg')
    # 0x0a ist the hex command to print a \n (new line)
    os.system('printf "\x1B@\x0a" | lp -d EPS')
    save_image_to_disk("original_img.jpg")

compliments = ["Skkr", "Sweet", "Total hottie!", "OK!", "Nice", "Uh", "Rrrr", "Marvellous", "Extraordinary", "Lovely!", "Magic!", "Handsome", 
    "Uh lala!", "Sheeeeesh!", "Oh Baby!", "Stunning!", "Gorgeous!", "Picture-perfect!", "Fantastic!", "Amazing!", "Dazzling!",
    "Captivating!", "Flawless!", "Beautiful!", "Wonderful!", "Impressive!", "Spectacular!", "Striking!", "Charming!", "Adorable!",
    "Enchanting!", "Dangerous!"
    ]
def generate_compliment_frame():
    text = random.choice(compliments)
    im = Image.new("RGBA", (screen_width, screen_height), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    draw_cam_overlay(d)

    fnt = ImageFont.truetype(font_path, max(50, min(120, round(400/len(text)))))
    (left, top, right, bottom) = fnt.getbbox(text)
    txt=Image.new('RGBA', (right, bottom), (0,0,0,0))
    dt = ImageDraw.Draw(txt)
    dt.text( (0, 0), text,  font=fnt, fill=(255, 153, 255, 190))
    txt=txt.rotate(random.uniform(-35, 35),  expand=1)
    (tw, th) = txt.size
    im.paste(txt, (random.randrange(max(1,screen_width-tw)),random.randrange(max(1,screen_height-th-screen_overlay_bar_height))))
    return np.rot90(np.asarray(im), -1)


COUNTDOWN_SEC = 3
countdown_frames = []

for i in range(0, COUNTDOWN_SEC+1):
    if i == 0:
        countdown_frames.append(countdown_text("Cheese!", 80))
    else:
        countdown_frames.append(countdown_text(str(i), 300))

# clear printer queue
os.system("sudo cancel -a")
touch_input_controller = TouchInput(screen_width, screen_height)
touch_input_controller.start_async_touchscreen_capture()
settings = load_settings()
print(settings)
settings_screen = SettingsScreen(screen_width, screen_height, font_path, settings["brightness"], settings["contrast"])

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
# width and height are swapped
picam2.configure(picam2.create_preview_configuration({"size": (screen_height, screen_width)}))
picam2.start_preview(Preview.DRM, x=0, y=0, width=screen_height, height=screen_width, transform=Transform(hflip=1))
picam2.start()

state = "default"
countdown_number = 0
menu_visible_until = 0
countdown_running_until = 0
compliment_until = 0
last_time_settings_pressed = 0
cam_overlay_image = cam_overlay()
next_compliment = generate_compliment_frame()
picam2.set_overlay(cam_overlay_image)
while True:
    if state == "compliment" and time.perf_counter() > compliment_until:
        picam2.set_overlay(cam_overlay_image)
        state = "default"
    if countdown_running_until > time.perf_counter():
        current_countdown_number = round(countdown_running_until - time.perf_counter())
        # update countdown number
        if current_countdown_number != countdown_number:
            countdown_number = current_countdown_number
            picam2.set_overlay(countdown_frames[countdown_number])
    elif countdown_running_until != 0:
        picam2.set_overlay(next_compliment)
        state = "compliment"
        compliment_until = time.perf_counter() + 2
        countdown_running_until = 0
        picam2.capture_file("raw.jpg")
        process_image("raw.jpg")
        next_compliment = generate_compliment_frame()
    if state == "settings" and time.perf_counter() > menu_visible_until:
        picam2.set_overlay(cam_overlay_image)
        state = "default"
    if not touch_input_controller.down_events.empty():
        (x,y) = touch_input_controller.down_events.get()
        # trigger snapshot
        if x > trigger_x1 and y > trigger_y1 and x < trigger_x2 and y < trigger_y2 and state != "settings":
            countdown_running_until = time.perf_counter() + COUNTDOWN_SEC
            state = "default"
        # update because of changed settings
        if state == "settings" and settings_screen.tap_event(x,y):
            picam2.set_overlay(settings_screen.image_buffer)
            save_settings()
            menu_visible_until = time.perf_counter() + 5
        # open settings by double clicking upper left corner of screen
        elif x < 100 and y < 100:
            if time.perf_counter() - last_time_settings_pressed < 1:
                picam2.set_overlay(settings_screen.image_buffer)
                menu_visible_until = time.perf_counter() + 5
                state = "settings"
            last_time_settings_pressed = time.perf_counter()
    # reduce CPU usage
    time.sleep(0.01)