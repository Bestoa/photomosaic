from PIL import Image, ImageStat
import numpy as np
import os
import random


class Render:


    PIXEL_BLEND = 0
    FAST_PIXEL_BLEND = 1
    DIRECT_BLEND = 2

    def _get_next_pixel_image(self, size, brightness = 0):

        if self.fast_mode:
            f = random.choice(self.pixel_img_source_name_list)
            if f in self.pixel_img_source_dict:
                return self.pixel_img_source_dict[f]
            self.pixel_img_source_dict[f] = Image.open(f).resize(size)
            return self.pixel_img_source_dict[f]
        else:
            return self._get_next_pixel_image_with_brightness(size, brightness)


    def _get_next_pixel_image_with_brightness(self, size, brightness):

        if len(self.pixel_img_source_with_brightness_list) == 0:
            self._init_pixel_image_with_brightness_list(size)
        return random.choice(self._get_candidate_img_list(brightness))[0]


    def _get_candidate_img_list(self, brightness):
        tmp_list = []
        for items in self.pixel_img_source_with_brightness_list:
            tmp_list.append((items[0], abs(brightness - items[1])))
        tmp_list.sort(key = lambda x : x[1])
        end = 0
        for index, items in enumerate(tmp_list):
            if items[1] > 20:
                end = index
                break
        if end < 5:
            end = 5
        return tmp_list[:end]


    def _init_pixel_image_with_brightness_list(self, size):

        print('Init pixel image brightness list')
        for f in self.pixel_img_source_name_list:
            img = Image.open(f).resize(size)
            self.pixel_img_source_with_brightness_list.append((img, ImageStat.Stat(img.convert('L')).mean[0]))


    def _get_pixel_brightness(self, pixel):
        return pixel[0] * 0.3 + pixel[1] * 0.59 + pixel[2] * 0.11


    def _pixel_blend_mode(self):

        if self.self_mode:
            pixel_img = self.img.resize((self.pixel_size, self.pixel_size))

        target_pixel_img = self.img.resize((int(self.img.width * self.scale / self.pixel_size), int(self.img.height * self.scale / self.pixel_size)), resample = Image.LANCZOS)
        target_pixel_img_arr = np.asarray(target_pixel_img)
        target_img = Image.new('RGB', (target_pixel_img.width * self.pixel_size, target_pixel_img.height * self.pixel_size), (0, 0, 0))

        for h_offset, line in enumerate(target_pixel_img_arr):
            for w_offset, pixel in enumerate(line):
                pixel_color_img = Image.new('RGB', (self.pixel_size, self.pixel_size), tuple(pixel))
                if not self.self_mode:
                    pixel_img = self._get_next_pixel_image((self.pixel_size, self.pixel_size), self._get_pixel_brightness(pixel))
                final_pixel_img = Image.blend(pixel_img, pixel_color_img, self.blend_fact)
                target_img.paste(final_pixel_img, (w_offset  * self.pixel_size, h_offset * self.pixel_size, (w_offset + 1) * self.pixel_size, (h_offset + 1) * self.pixel_size))

        return target_img


    def _direct_blend_mode(self):

        if self.self_mode:
            pixel_img = self.img.resize((self.pixel_size, self.pixel_size))

        target_w = int(self.img.width / self.pixel_size) * self.scale
        target_h = int(self.img.height / self.pixel_size) * self.scale

        target_img  = self.img.resize((target_w * self.pixel_size, target_h * self.pixel_size), resample = Image.LANCZOS)
        target_img_source = Image.new('RGB', (target_w * self.pixel_size, target_h * self.pixel_size), (0, 0, 0))

        x, y = 0, 0
        while x < target_h:
            y = 0
            while y < target_w:
                if not self.self_mode:
                    pixel_img = self._get_next_pixel_image((self.pixel_size, self.pixel_size))
                target_img_source.paste(pixel_img, (y * self.pixel_size, x * self.pixel_size, (y + 1) * self.pixel_size, (x + 1) * self.pixel_size))
                y += 1
            x += 1
        return Image.blend(target_img_source, target_img, self.blend_fact)


    def blend(self):
        return self._blend()


    def __init__(self, filename, mode,  pixel_size, scale, blend_fact, path):

        if path == None:
            self.self_mode = True
        else:
            self.self_mode = False
            self.pixel_img_source_name_list = []
            self.pixel_img_source_dict = {}
            for f in  os.listdir(path):
                self.pixel_img_source_name_list.append(path + '/' + f)

        self.img = Image.open(filename)
        self._blend = lambda : None
        self.fast_mode = True
        if mode == Render.PIXEL_BLEND:
            self._blend = self._pixel_blend_mode
            self.fast_mode = False
        elif mode == Render.FAST_PIXEL_BLEND:
            self._blend = self._pixel_blend_mode
        elif mode == Render.DIRECT_BLEND:
            self._blend = self._direct_blend_mode

        if self.self_mode and not self.fast_mode:
            print("Can't use non-fast blend mode when pixel image is self")
            self.fast_mode = True
        else:
            self.pixel_img_source_with_brightness_list = []

        self.pixel_size = pixel_size
        self.scale = scale
        self.blend_fact = blend_fact

