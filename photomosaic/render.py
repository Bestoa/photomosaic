from PIL import Image, ImageStat
from cachetools import LRUCache
import numpy as np
import os
import random


class Render:


    FAST_MODE = 1
    PIXEL_BLEND = 1 << 16
    DIRECT_BLEND = 1 << 17
    SIMPLE_BLEND = 1 << 18

    def _get_pixel_image_cached(self, name, size):

        if name in self.LRU_pixel_image_dict:
            return self.LRU_pixel_image_dict[name]
        self.LRU_pixel_image_dict[name] = Image.open(name).resize(size)
        return self.LRU_pixel_image_dict[name]


    def _get_next_pixel_image(self, size, brightness = 0):

        if self.config['fast mode']:
            name = random.choice(self.pixel_img_source_name_list)
            return self._get_pixel_image_cached(name, size)
        else:
            return self._get_next_pixel_image_with_brightness(size, brightness)


    def _get_next_pixel_image_with_brightness(self, size, brightness):

        name = random.choice(self._get_candidate_img_list(brightness))
        return self._get_pixel_image_cached(name, size)


    def _get_candidate_img_list(self, brightness):

        candidate_img_list = []
        backup_img_list = []
        for items in self.pixel_img_source_name_list:
            brightness_delta = abs(brightness - items[1])
            if brightness_delta < 25:
                candidate_img_list.append(items[0])
            else:
                backup_img_list.append((items[0], brightness_delta))
        if len(candidate_img_list) == 0:
            candidate_img_list.append(min(backup_img_list, key = lambda x : x[1])[0])
        return candidate_img_list


    def _get_pixel_brightness(self, pixel):

        if self.config['fast mode']:
            return 0
        return pixel[0] * 0.3 + pixel[1] * 0.59 + pixel[2] * 0.11


    def _get_area_brightness(self, img, area):

        if self.config['fast mode']:
            return 0
        return ImageStat.Stat(img.crop(area).convert('L')).mean[0]


    def _pixel_blend_mode(self):

        pixel_w, pixel_h = self.config['pixel size']

        if self.config['self mode']:
            pixel_img = self.img.resize((pixel_w, pixel_h))

        target_pixel_img = self.img.resize((int(self.img.width * self.config['scale'] / pixel_w), int(self.img.height * self.config['scale'] / pixel_h)), resample = Image.LANCZOS)
        target_pixel_img_arr = np.asarray(target_pixel_img)
        target_img = Image.new('RGB', (target_pixel_img.width * pixel_w, target_pixel_img.height * pixel_h), (0, 0, 0))

        for h_offset, line in enumerate(target_pixel_img_arr):
            for w_offset, pixel in enumerate(line):
                pixel_color_img = Image.new('RGB', (pixel_w, pixel_h), tuple(pixel))
                if not self.config['self mode']:
                    pixel_img = self._get_next_pixel_image((pixel_w, pixel_h), self._get_pixel_brightness(pixel))
                final_pixel_img = Image.blend(pixel_img, pixel_color_img, self.config['blend fact'])
                target_img.paste(final_pixel_img, (w_offset  * pixel_w, h_offset * pixel_h, (w_offset + 1) * pixel_w, (h_offset + 1) * pixel_h))

        return target_img


    def _direct_blend_mode(self):

        pixel_w, pixel_h = self.config['pixel size']

        if self.config['self mode']:
            pixel_img = self.img.resize((pixel_w, pixel_h))

        target_w = int(self.img.width / pixel_w) * self.config['scale']
        target_h = int(self.img.height / pixel_h) * self.config['scale']

        target_img  = self.img.resize((target_w * pixel_w, target_h * pixel_h), resample = Image.LANCZOS)
        target_img_source = Image.new('RGB', (target_w * pixel_w, target_h * pixel_h), (0, 0, 0))

        x, y = 0, 0
        while x < target_h:
            y = 0
            while y < target_w:
                target_area = (y * pixel_w, x * pixel_h, (y + 1) * pixel_w, (x + 1) * pixel_h)
                if not self.config['self mode']:
                    pixel_img = self._get_next_pixel_image((pixel_w, pixel_h), self._get_area_brightness(target_img, target_area))
                target_img_source.paste(pixel_img, target_area)
                y += 1
            x += 1
        return Image.blend(target_img_source, target_img, self.config['blend fact'])


    def _simple_blend_mode(self):

        pixel_w, pixel_h = self.config['pixel size']
        source_w = int(self.img.width / pixel_w)
        source_h = int(self.img.height / pixel_h)
        target_w = int(source_w * pixel_w * self.config['scale'])
        target_h = int(source_h * pixel_h * self.config['scale'])
        return  self.img.resize((source_w, source_h)).resize((target_w, target_h))


    def blend(self):
        return self._blend()


    def __init__(self, img, mode, pixel_size, scale, blend_fact, resource_path):

        self.config = {}
        if resource_path == None:
            self.config['self mode'] = True
        else:
            self.config['self mode'] = False
            self.pixel_img_source_name_list = []
            self.LRU_pixel_image_dict = LRUCache(maxsize = 512)
            for f in  os.listdir(resource_path):
                self.pixel_img_source_name_list.append(os.path.join(resource_path, f))

        self.img = img
        self._blend = lambda : None
        self.config['fast mode'] = False

        if mode & Render.PIXEL_BLEND:
            self.config['blend mode'] = 'Pixel'
            self._blend = self._pixel_blend_mode
        elif mode & Render.DIRECT_BLEND:
            self.config['blend mode'] = 'Direct'
            self._blend = self._direct_blend_mode
        elif mode & Render.SIMPLE_BLEND:
            self.config['blend_mode'] = 'Simple'
            self._blend = self._simple_blend_mode

        if mode & Render.FAST_MODE:
            self.config['fast mode'] = True

        if self.config['self mode'] and not self.config['fast mode']:
            print("Can't use non-fast blend mode when pixel image is self")
            self.config['fast mode'] = True

        if self.config['fast mode'] == False:
            self.pixel_img_source_name_list = list(map(lambda x : (x, ImageStat.Stat(Image.open(x).convert('L')).mean[0]), self.pixel_img_source_name_list))

        self.config['pixel size'] = pixel_size
        self.config['scale'] = scale
        self.config['blend fact'] = blend_fact
        print('config = ', self.config)

