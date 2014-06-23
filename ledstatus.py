import os
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import subprocess


class LedStatus:
    def __init__(self):
        self.processes = set()
        self.set_status()

    @staticmethod
    def set_status(text=None, bgcolor='black'):
        if not text:
            text = [("Raspberry Pi ", (255, 0, 0))]
        font = ImageFont.truetype(os.path.dirname(os.path.realpath(__file__)) + '/C&C Red Alert [INET].ttf', 13)
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

    def display(self):
        command = ['./led-matrix', '1', 'status.ppm']
        self.reset_display()

        self.processes.add(
            subprocess.Popen(command,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE))

    def reset_display(self):
        for p in self.processes:
            (stdout_data, stderr_data) = p.communicate(input='\n')
            if not stderr_data:
                print stderr_data
        self.processes = set()