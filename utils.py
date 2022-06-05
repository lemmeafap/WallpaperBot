from PIL import Image, ImageDraw, ImageFont


def watermark_text(image_name):
    im = Image.open(image_name)
    drawing = ImageDraw.Draw(im)
    color = (255,255,255,255)
    font = ImageFont.truetype('SupermercadoOne-Regular.ttf', 48)
    drawing.text((0,0), '@You_favorite_wallpapersBot', fill=color, font=font)
    im.save(f'water_{image_name}')

def crop_image_to_mobile(image_path):
    with Image.open(image_path) as im:
        original_height = im.size[0]
        height = im.size[1]
        width = height // 2
        (left, upper, right, lower) = ((original_height - width) // 2 ,
                                       0,
                                       (original_height + width) // 2,
                                       height)

        im_crop = im.crop((left, upper, right, lower))
        im_crop.save(f'crop_{image_path}', quality=100)