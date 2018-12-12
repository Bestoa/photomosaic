from PIL import Image
import numpy as np
import os
import random

PIXEL_BLEND = 1
DIRECT_BLEND = 2

def pixel_blend_mode(img, pixsize, scale, blend_fact, self_mode):

    if self_mode:
        pix_img = img.resize((pixsize, pixsize))

    target_pix_img = img.resize((int(img.width * scale / pixsize), int(img.height * scale / pixsize)), resample = Image.LANCZOS)
    target_pix_img_arr = np.asarray(target_pix_img)
    target_img = Image.new('RGB', (target_pix_img.width * pixsize, target_pix_img.height * pixsize), (0, 0, 0))

    for h_offset, line in enumerate(target_pix_img_arr):
        for w_offset, pix in enumerate(line):
            pix_color_img = Image.new('RGB', (pixsize, pixsize), tuple(pix))
            if not self_mode:
                pix_img = get_next_pixel_image(pixsize, pixsize)
            new_pix_img = Image.blend(pix_img, pix_color_img, blend_fact)
            target_img.paste(new_pix_img, (w_offset  * pixsize, h_offset * pixsize, (w_offset + 1) * pixsize, (h_offset + 1) * pixsize))

    return target_img

def direct_blend_mode(img, pixsize, scale, blend_fact, self_mode):

    if self_mode:
        pix_img = img.resize((pixsize, pixsize))

    target_w = int(img.width/pixsize) * scale
    target_h = int(img.height/pixsize) * scale

    target_img  = img.resize((target_w * pixsize, target_h * pixsize), resample = Image.LANCZOS)
    target_img_source = Image.new('RGB', (target_w * pixsize, target_h * pixsize), (0, 0, 0))

    x, y = 0, 0
    while x < target_h:
        y = 0
        while y < target_w:
            if not self_mode:
                pix_img = get_next_pixel_image(pixsize, pixsize)
            target_img_source.paste(pix_img, (y * pixsize, x * pixsize, (y + 1) * pixsize, (x + 1) * pixsize))
            y += 1
        x += 1
    return Image.blend(target_img_source, target_img, blend_fact)


img_list = dict() 
img_name_list = []


def get_next_pixel_image(w, h):
    f = random.choice(img_name_list)
    if f in img_list:
        return img_list[f]
    img_list[f] = Image.open(f).resize((w, h))
    return img_list[f]


def gen_image(filename, mode = PIXEL_BLEND, pixsize = 8, scale = 1, blend_fact = 0.75, path = None):

    self_mode = False
    if path == None:
        self_mode = True
    else:
        file_list = os.listdir(path)
        for f in file_list:
            img_name_list.append(path + '/' + f)

    img = Image.open(filename)

    if mode == PIXEL_BLEND:
        return pixel_blend_mode(img, pixsize, scale, blend_fact, self_mode)
    elif mode == DIRECT_BLEND:
        return direct_blend_mode(img, pixsize, scale, blend_fact, self_mode)

