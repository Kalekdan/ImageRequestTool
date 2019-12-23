from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from flask import Flask, request, send_file
import os.path

app = Flask(__name__)

f = open("helpPage.html", "r")
helpHTML = f.read()
f.close()


@app.route('/get-custom-image')
def query_example():
    # Get the GET request arguments
    image = request.args.get('img')  # if image doesn't exist, returns None
    if image is None:
        return helpHTML
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


# Generate a custom file name to specify a specific image and parameters used
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


# Return true if the image already exists using the parameters specified else return false
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
    im = saveImageAsType(im, newImgName, type)
    return im


# Resize the image to the x, y values provided
def resizeImage(imageToResize, x, y):
    size = x, y
    return imageToResize.resize(size, Image.ANTIALIAS)


# Add a watermark to the image
def addWaterMark(image, text):
    # make the image editable
    image_drawing = ImageDraw.Draw(image)
    black = (3, 8, 12)
    font = getFontAutoSized(image, text, .8)
    W, H = image.size
    w, h = image_drawing.textsize(text, font=font)
    # Write text on image
    image_drawing.text(((W - w) / 2, (H - h) / 2), text, fill=black, font=font)
    return image


# Returns the font that is the correct size to take up the specified fraction of the image
def getFontAutoSized(image, txt, fraction):
    fontsize = 1
    font = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", fontsize)
    while font.getsize(txt)[0] < fraction * image.size[0]:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", fontsize)
    return font


# Add a background color to the image
def addBackgroundColor(image, color):
    # Generate a new image of the same size and fill it with color
    background = Image.new("RGBA", (image.size[0], image.size[1]))
    bgDraw = ImageDraw.Draw(background)
    bgDraw.rectangle(((0, 00), (image.size[0], image.size[1])), fill='#' + color)
    # Return new composite image of base image + color background
    return Image.alpha_composite(background, image)


# Saves the image with the name provided
def saveImageAsType(image, name, type):
    # if type is jpeg, remove transparency before saving
    if type == 'jpeg':
        image = image.convert('RGB')
    image.save('imgCache/' + name, type)
    return image


if __name__ == '__main__':
    app.run(debug=True, port=5000)  # run app in debug mode on port 5000
