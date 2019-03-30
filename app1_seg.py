import numpy as np
import json
from skimage import io, data
from PIL import Image


import dash_canvas
import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate

from dash_canvas.utils import  (parse_jsonstring, segmentation_generic,
                               image_with_contour, image_string_to_PILImage)
from dash_canvas.components import image_upload_zone

# Image to segment and shape parameters
filename = 'https://upload.wikimedia.org/wikipedia/commons/e/e4/Mitochondria%2C_mammalian_lung_-_TEM_%282%29.jpg'
try:
    img = io.imread(filename, as_gray=True)
except:
    img = data.coins()
height, width = img.shape
canvas_width = 500
canvas_height = round(height * canvas_width / width)
scale = canvas_width / width


# ------------------ App definition ---------------------

def title():
    return "Supervized segmentation"


def description():
    return "Segmentation of objects from annotations"


layout = html.Div([
    html.Div([
        dcc.Tabs(
            id='segmentation-tabs',
            value='segmentation-canvas-tab',
            children=[
                dcc.Tab(
                    label='Annotation tool',
                    value='segmentation-canvas-tab',
                    children=[
                        dash_canvas.DashCanvas(
                            id='canvas',
                            width=canvas_width,
                            height=canvas_height,
                            scale=scale,
                            filename=filename,
                            goButtonTitle='Segmentation'
                        ),
                        image_upload_zone('upload-image'),

                ]),
                dcc.Tab(
                    label='Segmentation result',
                    value='segmentation-result-tab',
                    children=[
                        dcc.Graph(
                        id='segmentation',
                        figure=image_with_contour(np.ones_like(img),
                                    img > 0, shape=(height, width))
                        )
                    ]),
                dcc.Tab(
                     label='How to use this app',
                     value='segmentation-help-tab',
                     children=[
                        html.Img(id='segmentation-help',
                                 src='assets/segmentation.gif',
                                 width='100%'),
                     ]
                )
        ]
        ),
    ], className="seven columns"),
    html.Div([
        html.H2(children='Segmentation tool'),
        dcc.Markdown('''
                Draw on the picture to annotate each object
                you want to segment, then press the "Segmentation"
                button to trigger the segmentation.
            '''),
        html.Br(),
        html.Label('Segmentation alorithm'),
        dcc.Dropdown(
            id='algorithm',
            options=[
                    {'label': 'Watershed', 'value': 'watershed'},
                    {'label': 'Random Walker', 'value': 'random_walker'},
                    {'label': 'Random Forest', 'value': 'random_forest'}
                ],
                value='watershed'
            ),
        ], className="five columns")],# Div
    className="row")

# ----------------------- Callbacks -----------------------------


def callbacks(app):
    @app.callback(Output('segmentation', 'figure'),
                [Input('canvas', 'json_data')],
                [State('canvas', 'image_content'),
                State('algorithm', 'value')])
    def update_figure_upload(string, image, algorithm):
        print("update figure")
        if string:
            if image is None:
                im = img
                image = img
            else:
                im = image_string_to_PILImage(image)
                im = np.asarray(im)
            shape = im.shape[:2]
            mask = parse_jsonstring(string, shape=shape)
            if mask.sum() > 0:
                seg = segmentation_generic(im, mask, mode=algorithm)
            else:
                seg = np.zeros(shape)
            return image_with_contour(im, seg, shape=shape)
        else:
            raise PreventUpdate



    @app.callback(Output('canvas', 'image_content'),
                [Input('upload-image', 'contents')])
    def update_canvas_upload(image_string):
        print("uploading", image_string[:100])
        if image_string is None:
            raise PreventUpdate
        else:
            return image_string


    @app.callback(Output('segmentation-tabs', 'value'),
                  [Input('canvas', 'json_data')])
    def change_focus(string):
        if string:
            return 'segmentation-result-tab'
        return 'segmentation-canvas-tab'
