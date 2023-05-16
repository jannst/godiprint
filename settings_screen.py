from PIL import Image, ImageDraw, ImageFont
import numpy as np

class SettingsScreen:

    def __init__(self, screen_width, screen_height, font_path, brightness, contrast):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.controls_font = ImageFont.truetype(font_path, 100) 
        self.headline_font = ImageFont.truetype(font_path, 80)
        self.normal_font = ImageFont.truetype(font_path, 50)
        self.small_font = ImageFont.truetype(font_path, 25)

        self.canvas = Image.new("RGBA", (screen_width, screen_height), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.canvas)

        self.buttons = []
        self.brightness = brightness
        self.contrast = contrast
        self.render()


    def x_centered_pos(self, font, text):
        (left, top, right, bottom) = font.getbbox(text)
        text_width = right-left
        return self.screen_width/2-text_width/2

    def draw_control_box(self, y, id, pressed=False, is_decrease=True):
        box_s = 70
        x = 80 if is_decrease else 330
        transparency = 200 if pressed else 100
        self.draw.rectangle((x, y, x+box_s, y+box_s), fill=(255, 153, 255, transparency), outline=(255, 255, 255))
        self.buttons.append((id, x, y, x+box_s, y+box_s))
        offset_x = 25 if is_decrease else 10
        offset_y = 25 if is_decrease else 25
        text = "-" if is_decrease else "+"
        self.draw.text((x+offset_x, y-offset_y), text, font=self.controls_font, fill=(255, 255, 255))

    def tap_event(self, x, y):
        for (id, x1, y1, x2, y2) in self.buttons:
            if x >= x1 and x <= x2 and y >= y1 and y <= y2:
                if id == "C_UP":
                    self.contrast = min(self.contrast+0.05, 3)
                    self.render()
                    return True
                elif id == "C_DOWN":
                    self.contrast = max(self.contrast-0.05, 0)
                    self.render()
                    return True
                elif id == "B_UP":
                    self.brightness = min(self.brightness+0.05, 3)
                    self.render()
                    return True
                elif id == "B_DOWN":
                    self.brightness = max(self.brightness-0.05, 0)
                    self.render()
                    return True
        return False


    def render(self):
        self.draw.rectangle((0,0, self.screen_width, self.screen_height), fill=(0,0,0,0))
        headline = "Settings <3"
        y=10
        self.draw.text((self.x_centered_pos(self.headline_font, headline), y), headline, font=self.headline_font, fill=(255, 153, 255, 190))

        y += 100
        note_text = "Changes apply to the printed pictures"
        self.draw.text((30, y), note_text, font=self.small_font, fill=(255, 153, 255, 190))
        y += 30
        note_text = "only and will not appear on screen."
        self.draw.text((30, y), note_text, font=self.small_font, fill=(255, 153, 255, 190))

        y += 70

        contrast_text = "Contrast"
        self.draw.text((self.x_centered_pos(self.normal_font, contrast_text), y), contrast_text, font=self.normal_font, fill=(255, 153, 255, 190))
        y +=60
        self.draw_control_box(y, "C_DOWN", False, True)
        self.draw_control_box(y, "C_UP", False, False)
        contrast_val_text = "{:.2f}".format(self.contrast)
        self.draw.text((self.x_centered_pos(self.normal_font, contrast_val_text), y), contrast_val_text, font=self.normal_font, fill=(255, 153, 255, 190))

        brightness_test = "Brightness"
        y +=110
        self.draw.text((self.x_centered_pos(self.normal_font, brightness_test), y), brightness_test, font=self.normal_font, fill=(255, 153, 255, 190))
        y += 60
        self.draw_control_box(y, "B_DOWN", False, True)
        self.draw_control_box(y, "B_UP", False, False)
        brightness_val_text = "{:.2f}".format(self.brightness)
        self.draw.text((self.x_centered_pos(self.normal_font, brightness_val_text), y), brightness_val_text, font=self.normal_font, fill=(255, 153, 255, 190))
            
        self.image_buffer = np.rot90(np.asarray(self.canvas), -1)