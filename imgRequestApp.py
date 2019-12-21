from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from flask import Flask, request, send_file
import os.path

app = Flask(__name__)


# TODO: fix bug with saving as jpeg

@app.route('/query-example')
def query_example():
    image = request.args.get('img')  # if image doesn't exist, returns None
    res = request.args.get('res')  # Takes parameter in format '1920x1080'
    if res is not None:
        res = res.split('x')
        res = list(map(int, res))
    bg_col = request.args.get('background')
    watermark = request.args.get('watermark')
    im_type = request.args.get('type', default='png')  # Returns png image if type not specified

    generated_img_name = generateFileName(image, res, im_type, bg_col, watermark)

    # If image exists in cache, return image
    if imageExistsInCache(generated_img_name):
        return send_file('imgCache/' + generated_img_name)
    # If no image exists in cache create edited image
    else:
        # Check if base image exists
        base_img_name = image + '.png'
        if not imageExistsInCache(base_img_name):
            return '''<h1>Image does not exist:''' + image + '.png' + ''' </h1>'''
        else:  # Image exists but not with specified parameters
            generateNewImg(base_img_name, generated_img_name, res, im_type, bg_col, watermark)
            # Send the newly generated image to user
            return send_file('imgCache/' + generated_img_name)


@app.route('/form-example')
def formexample():
    return 'Todo...'


@app.route('/json-example')
def jsonexample():
    return 'Todo...'


def generateFileName(imageName, resolution, type, bgCol, wtmk):
    if resolution is None:
        resStr = ''
    else:
        resStr = '_r' + str(resolution[0]) + 'x' + str(resolution[1])
    if bgCol is None:
        bgColStr = ''
    else:
        bgColStr = '_bg' + bgCol
    if wtmk is None:
        wtmkStr = ''
    else:
        wtmkStr = '_w' + wtmk
    return imageName + resStr + bgColStr + wtmkStr + '.' + type;


def imageExistsInCache(filename):
    return os.path.exists('imgCache/' + filename)


# Generate a new image using the parameters provided and save to image cache
def generateNewImg(baseImgName, newImgName, resolution, type, bgCol, wtmk):
    im = Image.open('imgCache/' + baseImgName)
    if resolution is not None:
        im = resizeImage(im, resolution[0], resolution[1])
    if wtmk is not None:
        im = addWaterMark(im, wtmk)
    if bgCol is not None:
        im = addBackgroundColor(im, bgCol)
    im.save('imgCache/' + newImgName, type)
    return im


def resizeImage(imageToResize, x, y):
    size = x, y
    return imageToResize.resize(size, Image.ANTIALIAS)


def addWaterMark(image, text):
    # make the image editable
    image_drawing = ImageDraw.Draw(image)
    black = (3, 8, 12)
    font = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 40)
    W, H = image.size
    w, h = image_drawing.textsize(text, font=font)
    image_drawing.text(((W - w) / 2, (H - h) / 2), text, fill=black, font=font)
    return image


def addBackgroundColor(image, color):
    background = Image.new("RGBA", (image.size[0], image.size[1]))
    bgDraw = ImageDraw.Draw(background)
    bgDraw.rectangle(((0, 00), (image.size[0], image.size[1])), fill='#' + color)
    return Image.alpha_composite(background, image)


if __name__ == '__main__':
    app.run(debug=True, port=5000)  # run app in debug mode on port 5000
