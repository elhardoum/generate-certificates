from flask import Flask, request, render_template, Response
from config import *
from re import sub, search
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from base64 import b64decode, b64encode
from json import dumps
from os.path import isfile, basename
from glob import glob

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_SECRET
app.config['DEBUG'] = DEBUG

@app.route('/')
def index():
    fonts = [ sub('\.ttf$', '', basename(x)) for x in glob('./fonts/*.ttf') ]

    return render_template('index.html', max_file_size=TEMPLATE_MAX_FILESIZE, fonts=fonts)

@app.route('/xhr', methods=['GET', 'POST'])
def xhr():
    names, fontsize, color, template, top_percent = [], DEFAULT_FONTSIZE, None, None, DEFAULT_TOP_PERCENT
    font_family = 'Impact'

    if 'names' in request.form and request.form['names']:
        names = request.form['names'].split('\n')
        names = [ x.strip() for x in names if x ]
        names = [ x for x in names if x ]

    if 'fontsize' in request.form and str(request.form['fontsize']).isnumeric() and int(request.form['fontsize']) > 0:
        fontsize = int(request.form['fontsize'])

    try:
        if 'top_percent' in request.form and float(request.form['top_percent']) > 0:
            top_percent = float(request.form['top_percent'])
    except Exception: pass

    if 'color' in request.form and request.form['color']:
        if search( '^#(?:[0-9a-fA-F]{3}){1,2}$', request.form['color'].strip() ):
            color = request.form['color'].strip()

    if 'template' in request.form and request.form['template'].strip():
        template = request.form['template'].strip()

    if 'font_family' in request.form and request.form['font_family'].strip():
        font_family = request.form['font_family'].strip()

    errors = []

    if not len(names): errors.append( 'Please enter at least 1 name.' )
    if not fontsize: errors.append( 'Please enter a font size.' )
    if not color: errors.append( 'Please choose a font color.' )
    if not template: errors.append( 'Please submit a template image.' )

    if len(errors):
        return Response(response=dumps({'success': False, 'errors': errors}), status=200, mimetype='application/json')
    
    try:
        image_data = sub('^data:image/.+;base64,', '', template)
        image = Image.open(BytesIO(b64decode( image_data )))
        errors.append('Could not load your template image.')
    except Exception as e:
        return Response(response=dumps({'success': False, 'errors': errors}), status=200, mimetype='application/json')

    font_family = sub('[^a-zA-Z-_ ]', '', font_family)
    font_path = './fonts/%s.ttf' % font_family
    font_path = font_path if isfile( font_path ) else './fonts/Impact.ttf'

    print ( "\n\n", font_path, font_family, "\n\n" )

    font = ImageFont.truetype( font_path, fontsize )
    images = [ process_image( image.copy(), font, name, color, top_percent ) for name in names ]

    return Response(response=dumps({'success': True, 'images': images}), status=200, mimetype='application/json')

def process_image(image, font, text, color, top_percent):
    draw = ImageDraw.Draw(image)

    textWidth, textHeight = draw.textsize(text, font)
    x = image.size[0]/2 - textWidth/2
    y = int( image.size[1] * top_percent *0.01 )

    draw.text((x, y), text, color, font=font)

    buffered = BytesIO()
    image.save(buffered, format='PNG')
    return 'data:image/png;base64,%s' % b64encode(buffered.getvalue()).decode('utf-8')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
