import os
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw


class LedStatus:
    def __init__(self):
        self.set_status()

    @staticmethod
    def set_status(text=None, bgcolor='black'):
        if not text:
            text = [("Raspberry Pi ", (255, 0, 0))]
        font = ImageFont.truetype(os.path.dirname(os.path.realpath(__file__)) + '/C&C Red Alert [INET].ttf', 14)
        # font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSans.ttf", 16)
        all_text = ''
        for text_color_pair in text:
            t = text_color_pair[0]
            all_text += t + ' '

        width, ignore = font.getsize(all_text)

        img = Image.new('RGB', (max(width, 32), 16), bgcolor)
        draw = ImageDraw.Draw(img)

        x = 0
        for text_color_pair in text:
            t = text_color_pair[0]
            c = text_color_pair[1]
            draw.text((x, 2), t, c, font=font)
            x = x + font.getsize(t)[0]

        img.save('status.ppm')

    @staticmethod
    def display():
        os.system("./led-matrix 1 status.ppm")
