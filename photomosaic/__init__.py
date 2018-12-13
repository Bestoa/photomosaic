from render import Render

PIXEL_BLEND = Render.PIXEL_BLEND
DIRECT_BLEND = Render.DIRECT_BLEND

def gen_image(filename, mode = PIXEL_BLEND, pixel_size = 8, scale = 1, blend_fact = 0.75, path = None):
    r = Render(filename, mode, pixel_size, scale, blend_fact, path)
    return r.blend()

