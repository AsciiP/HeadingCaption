from PIL import Image, ImageDraw, ImageFont, ImageColor
import pysubs2
import os, sys
import yaml

# Load file and check if it's a valid subtitle file

sub_file = pysubs2.load(sys.argv[1])
if not sub_file:
    print('File not found or not a valid subtitle file.')
    exit()

# Load style file

styles = {}
for name in os.listdir('./styles/'):
    for file in os.listdir('./styles/' + name):
        if file == 'style.yaml' or file == 'style.yml':
            with open('./styles/' + name + '/' + file, 'r',
                      encoding='utf-8') as f:
                style = yaml.load(f, Loader=yaml.FullLoader)
            if style['logo']:
                style['logo'] = './styles/' + name + '/' + style['logo']
            if style['font_name']:
                style['font_name'] = './fonts/' + style['font_name']
            styles[name] = style

del name, file, style

# Load config file

with open('./config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

width = config['width']
height = config['height']
framerate = config['framerate']
row_spacing = config['row_spacing']

# Preload font file

fonts = {}
for style in styles.values():
    font = str(style['font_name'])
    if font not in fonts:
        fonts[font] = ImageFont.truetype(font, style['font_size'])

del style, font

# Preload logo image

logos = {}
for style in styles.values():
    if style['logo']:
        logo = str(style['logo'])
        if logo not in logos:
            logos[logo] = Image.open(style['logo']).convert('RGBA')

del style, logo

# Preload empty image

empty = Image.new(mode='RGBA', size=(width, height), color=(0, 0, 0, 0))

# Draw texts from an empty image, return an Image object


def draw_texts(subtitles: list):
    text_image = empty.copy()
    y_delta = 0

    for subtitle in subtitles:
        caption = subtitle[0]
        name = subtitle[1]

        style = styles[name]

        image_draw = ImageDraw.Draw(text_image)

        # Calculate coordinates
        margin = style['bg_margin']
        if style['logo']:
            logo = logos[style['logo']]
            logo_width = logo.width
            logo_height = logo.height
            logo_spacing = style['logo_spacing']
            text_x = style['x'] + (logo_width + logo_spacing) / 2
            text_y = style['y'] - y_delta

            text_box = image_draw.textbbox(xy=(text_x, text_y),
                                           text=caption,
                                           font=fonts[style['font_name']],
                                           anchor=style['anchor'],
                                           stroke_width=style['stroke_width'])

            logo_x = int(text_box[0] - logo_spacing - logo_width)
            logo_y = int(text_box[3] + margin - logo_height)
            rect_xy = (text_box[0] - logo_spacing - logo_width - margin,
                       text_box[1] - margin, text_box[2] + margin,
                       text_box[3] + margin)

        else:
            text_x = style['x']
            text_y = style['y'] - y_delta
            text_box = image_draw.textbbox(xy=(text_x, text_y),
                                           text=caption,
                                           font=fonts[style['font_name']],
                                           anchor=style['anchor'],
                                           stroke_width=style['stroke_width'])
            rect_xy = (text_box[0] - margin, text_box[1] - margin,
                       text_box[2] + margin, text_box[3] + margin)

        y_delta += text_box[3] - text_box[1] + margin * 2 + row_spacing

        # Draw rectangle background
        image_draw.rounded_rectangle(xy=rect_xy,
                                     radius=style['bg_radius'],
                                     fill=ImageColor.getrgb(style['bg_color']))

        # Draw text
        image_draw.text(xy=(text_x, text_y),
                        text=caption,
                        font=fonts[style['font_name']],
                        fill=ImageColor.getrgb(style['font_color']),
                        anchor=style['anchor'],
                        stroke_width=style['stroke_width'],
                        stroke_fill=ImageColor.getrgb(style['stroke_color']))

        if style['logo']:
            text_image.paste(logo, (logo_x, logo_y), logo)

    return text_image


# Generate a time line like flow events

time_line = {}  # {time(int): [action, caption, name]}
for line in sub_file:
    if line.text:
        if line.start not in time_line:
            time_line[line.start] = []
        if line.end not in time_line:
            time_line[line.end] = []
        time_line[line.start].append(['start', line.text, line.name])
        time_line[line.end].append(['end', line.text, line.name])

# Sort timeline by key
time_line = dict(sorted(time_line.items(), key=lambda item: item[0]))

# Generate images

current = []
clear = []
clips = []
for time in time_line:
    for event in time_line[time]:
        if event[0] == 'start':
            current.append(event[1:])
        elif event[0] == 'end':
            current.remove(event[1:])
    if current:
        image = draw_texts(current)
        image.save('./out/' + str(time) + '.png')
        clips.append(time)
    else:
        print('Clear at ' + str(time) + 'ms')
        clips.append(time)
        clear.append(time)

# Generate XML


def ms2frame(ms: int, framerate: int) -> int:
    return int(ms / 1000 * framerate)


with open('./out/timeline.xml', 'w', encoding='utf-8') as xml_file:
    with open('./templates/head.xml', 'r', encoding='utf-8') as head:
        xml_file.write(head.read().format(FRAMERATE=framerate,
                                          WIDTH=width,
                                          HEIGHT=height))
    with open('./templates/clip.xml', 'r', encoding='utf-8') as clip:
        c = clip.read()
        for i in range(len(clips)):
            if clips[i] not in clear:
                xml_file.write(
                    c.format(FILE=str(clips[i]) + '.png',
                             START=ms2frame(clips[i], framerate),
                             END=ms2frame(clips[i + 1], framerate),
                             PATH=os.path.abspath('./out/' + str(clips[i]) +
                                                  '.png').replace('\\', '/'),
                             FRAMERATE=framerate,
                             WIDTH=width,
                             HEIGHT=height))
            else:
                pass
    with open('./templates/foot.xml', 'r', encoding='utf-8') as foot:
        xml_file.write(foot.read())
