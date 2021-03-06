from .render import Render
from PIL import Image

__VERSION__ = '0.1.0'

def gen_image(filename_or_fp, mode = Render.PIXEL_BLEND, pixel_size = (8, 8), scale = 1, blend_fact = 0.75, resource_path = None):

    img = Image.open(filename_or_fp)
    return Render(img, mode, pixel_size, scale, blend_fact, resource_path).blend()

def auto_gen_image(filename_or_fp, pixel_size, resource_path, blend_mode = Render.PIXEL_BLEND):

    pixel_w, pixel_h = pixel_size
    img = Image.open(filename_or_fp)
    uniform_width = img.width / pixel_w
    uniform_height = img.height /pixel_h

    if uniform_width > uniform_height:
        uniform_width, uniform_height = _caculate_size(uniform_width, uniform_height)
    else:
        uniform_height, uniform_width = _caculate_size(uniform_height, uniform_width)

    scale = uniform_width * pixel_w / img.width
    return Render(img, blend_mode, pixel_size, scale, 0.75, resource_path).blend()


_target_w_h_min = 64
_target_w_h_max = 256

def _caculate_size(max_v, min_v):

    if max_v <= _target_w_h_max and min_v >= _target_w_h_min:
        return max_v, min_v
    elif max_v > _target_w_h_max:
        min_v = _target_w_h_max / max_v * min_v
        max_v = _target_w_h_max
        return max_v, min_v
    elif min_v < _target_w_h_min:
        max_v = _target_w_h_min / min_v * max_v
        min_v = _target_w_h_min
        return max_v, min_v

