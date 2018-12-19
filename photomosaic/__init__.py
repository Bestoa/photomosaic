from .render import Render

__VERSION__ = '0.0.1'

def gen_image(filename, mode = Render.PIXEL_BLEND, pixel_size = 8, scale = 1, blend_fact = 0.75, path = None):
    r = Render(filename, mode, pixel_size, scale, blend_fact, path)
    return r.blend()

