import numpy as np
import json
from skimage import io
from PIL import Image

import dash_canvas
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go

from dash_canvas.utils.parse_json import parse_jsonstring
from dash_canvas.utils.image_processing_utils import \
                                        superpixel_color_segmentation
from dash_canvas.utils.plot_utils import image_with_contour
from dash_canvas.utils.io_utils import image_string_to_PILImage, \
                                       array_to_data_url
from dash_canvas.components import image_upload_zone

# Image to segment and shape parameters
filename = './assets/dress.jpg'
filename_app = '/assets/dress.jpg'
img_app3 = io.imread(filename)
height, width, _ = img_app3.shape
print('app3', height, width)
canvas_width = 500
canvas_height = round(height * canvas_width / width)
scale = canvas_width / width


def title():
    return "Background removal"

def description():
    return "Remove background of image to extract objects of interest."


layout = html.Div([
    html.Div([
        html.Div([
            html.H2(children='Remove image background'),
            dcc.Markdown('''
             Draw on the object of interest, and press remove background.'''),
            dash_canvas.DashCanvas(
                id='canvas-bg',
                width=canvas_width,
                height=canvas_height,
                scale=scale,
                image_content=array_to_data_url(img_app3),
                lineWidth=4,
                goButtonTitle='Remove background',
                hide_buttons=['line', 'zoom', 'pan'],
            ),
            html.H6(children=['Brush width']),
            dcc.Slider(
                id='bg-width-slider',
                min=2,
                max=40,
                step=1,
                value=[5]
            ),
            image_upload_zone('upload-image-bg'),
        ], className="seven columns"),
        html.Div([
            html.H3(children='How to use this app and remove background',
                    id='bg-title'),
            html.Img(id='segmentation-bg',
                     src='assets/bg.gif',
                     width='100%')
        ], className="five columns")],
        className="row")
        ])

# ----------------------- Callbacks -----------------------------
def callbacks(app):


    @app.callback(Output('bg-title', 'children'),
                 [Input('canvas-bg', 'json_data')])
    def modify_bg_title(json_data):
        if json_data:
            return "Image without background"
        else:
            raise PreventUpdate


    @app.callback(Output('segmentation-bg', 'src'),
                  [Input('canvas-bg', 'json_data')],
                  [State('canvas-bg', 'image_content')])
    def update_figure_upload(string, image):
        if string:
            if image is None:
                im = img_app3
            else:
                im = image_string_to_PILImage(image)
                im = np.asarray(im)
            shape = im.shape[:2]
            try:
                mask = parse_jsonstring(string, shape=shape)
            except IndexError:
                raise PreventUpdate
            if mask.sum() > 0:
                seg = superpixel_color_segmentation(im, mask)
            else:
                seg = np.ones(shape)
            fill_value = 255 * np.ones(3, dtype=np.uint8)
            dat = np.copy(im)
            dat[np.logical_not(seg)] = fill_value
            return array_to_data_url(dat)
        else:
            raise PreventUpdate


    @app.callback(Output('canvas-bg', 'json_data'),
                [Input('canvas-bg', 'image_content')])
    def clear_data(image_string):
        return ''


    @app.callback(Output('canvas-bg', 'image_content'),
                [Input('upload-image-bg', 'contents')])
    def update_canvas_upload(image_string):
        if image_string is None:
            raise ValueError
        if image_string is not None:
            return image_string
        else:
            return None


    @app.callback(Output('canvas-bg', 'lineWidth'),
                [Input('bg-width-slider', 'value')])
    def update_canvas_linewidth(value):
        return value

