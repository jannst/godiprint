import evdev
import threading
import queue


class TouchInput:
    # these are are driver default provided by Waveshare.
    # See https://www.waveshare.com/wiki/5inch_HDMI_LCD
    # Also have a look inside the /boot/config.txt file
    # the following values are measured by hand
    xmin=300
    xmax=3900
    ymin=150
    ymax=4000

    down_events = queue.Queue()
    touchscreen_lock = threading.Lock()
    current_x = 0
    current_y = 0
    is_pressed = False

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update_touch_input(self, new_is_pressed, x, y):
        self.touchscreen_lock.acquire()
        try:
            if x is not None and y is not None and new_is_pressed:
                translation_x = (self.xmax-self.xmin)/self.screen_width
                translation_y = (self.ymax-self.ymin)/self.screen_height
                cropped_x = min(max(self.xmin, x), self.xmax)
                cropped_y = min(max(self.ymin, y), self.ymax)
                new_x = round((cropped_x-self.xmin) / translation_x)
                # inverted y
                new_y = self.screen_height - round((cropped_y-self.ymin) / translation_y)
                self.down_events.put((new_x, new_y))
        finally:
            self.touchscreen_lock.release()

    #def get_touch_input(self):
    #    self.touchscreen_lock.acquire()
    #    try: 
    #        return (self.current_x, self.current_y, self.is_pressed)
    #    finally :
    #        self.touchscreen_lock.release()


    def find_touchscreen(self):
        for device in [evdev.InputDevice(path) for path in evdev.list_devices()]:
            if device.name == "ADS7846 Touchscreen":
                return device

    def start_async_touchscreen_capture(self):
        self.capture_thread = threading.Thread(target = self.start_touchscreen_capture, args = ())
        self.capture_thread.start() 

    def start_touchscreen_capture(self):
        touchscreen_device = self.find_touchscreen()
        if touchscreen_device:
            print("Touchscreen input: ", touchscreen_device.path, touchscreen_device.name, touchscreen_device.phys)

            new_x = None
            new_y = None
            new_is_pressed = None

            # input constants from lineux kernel: https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
            for event in touchscreen_device.read_loop():
                # SYN event -> flush
                if event.type == 0x0 and event.code == 0x0 and event.value == 0x0:
                    self.update_touch_input(new_is_pressed, new_x, new_y)
                    new_x = None
                    new_y = None
                    new_is_pressed = None
                # BTN_TOUCH EVENT
                elif event.type == 0x01 and event.code == 0x14a:
                    if event.value:
                        new_is_pressed = True
                    else:
                        new_is_pressed = False
                # means it is an ABS event
                elif event.type == 0x03:
                    if event.code == 0x00:
                        new_x = event.value
                    elif event.code == 0x01:
                        new_y = event.value
                #print(type(evdev.categorize(event)), evdev.categorize(event), event)
        else:
            print("Touchscreen not found :(")