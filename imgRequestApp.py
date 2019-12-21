from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from flask import Flask, request, send_file
import os.path

app = Flask(__name__)

helpHTML = '''<style type="text/css">@media screen and (max-width: 767px) {.tg {width: auto !important;}.tg col {width: auto !important;}.tg-wrap {overflow-x: auto;-webkit-overflow-scrolling: touch;}}</style><div class="tg-wrap"><table style="border-collapse:collapse;border-spacing:0" class="tg"><tr><th style="font-family:Arial, sans-serif;font-size:14px;font-weight:bold;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">Key</th><th style="font-family:Arial, sans-serif;font-size:14px;font-weight:bold;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">Example Value</th><th style="font-family:Arial, sans-serif;font-size:14px;font-weight:bold;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">Description</th></tr><tr><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">img</td><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">02_04_2019_001158_2019-04-02-11-56-36<br></td><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">The file name (without extension) of the image you want to request<br><span style="font-style:italic">Request will fail if not specified</span></td></tr><tr><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">res</td><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">1920x1080</td><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">The horizontal and vertical resolution with an 'x' as a separater of the output desired.<br><span style="font-style:italic">Will retain original resolution if value not specified</span></td></tr><tr><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">background</td><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">FF1E1A</td><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">The background color to set on the image given as a hex code.<br><span style="font-style:italic">Will retain transparency if value not specified</span><br></td></tr><tr><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">watermark</td><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">This is a watermark</td><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">Adds a watermark to the image returned using the string provided<br><span style="font-style:italic">Will not add a watermark if value not specified</span><br></td></tr><tr><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">type</td><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">gif</td><td style="font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:black;text-align:left;vertical-align:top">The extension of the image type you would like returned<br><span style="font-style:italic">Returns image as '.png' if value not specified</span><br></td></tr></table></div>'''


# TODO: fix bug with saving as jpeg
# TODO: add auto text sizing for watermark

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
    im.save('imgCache/' + newImgName, type)
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
    font = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 40)
    W, H = image.size
    w, h = image_drawing.textsize(text, font=font)
    # Write text on image
    image_drawing.text(((W - w) / 2, (H - h) / 2), text, fill=black, font=font)
    return image


# Add a background color to the image
def addBackgroundColor(image, color):
    # Generate a new image of the same size and fill it with color
    background = Image.new("RGBA", (image.size[0], image.size[1]))
    bgDraw = ImageDraw.Draw(background)
    bgDraw.rectangle(((0, 00), (image.size[0], image.size[1])), fill='#' + color)
    # Return new composite image of base image + color background
    return Image.alpha_composite(background, image)


if __name__ == '__main__':
    app.run(debug=True, port=5000)  # run app in debug mode on port 5000
