import streamlit as st
import requests
from datetime import datetime
import pytz
import numpy as np
import pandas as pd
import streamlit.components.v1 as components


'''
# Autohome
'''


# if st.checkbox('Inject JAVA'):

#     components.html(
#         """
#                     <script src="../libs/opencv.min.js"></script>
#                     <video id="video-input" width="480px" height="320px></video>
#                     <canvas id="canvas-output" width="480px" height="320px></video>
#                     <script src="../javascript/opencv.js"></script>
#                     <p> oi </p>
#     """,
#         height=600,
#     )


# html_string = '''
# <head>
#   <meta charset="UTF-8" />
#   <meta http-equiv="X-UA-Compatible" content="IE=edge" />
#   <meta name="viewport" content="width=device-width, initial-scale=1.0" />
#   <title>OpenCV width JS</title>
#   <script src="../libs/opencv.min.js"></script>

#   <style>
#     #video-input,
#     #canvas-output {
#       border: 1px solid black;
#     }
#   </style>
# </head>
#   <label>Input CAM</label>
#   <video id="video-input" width="480px" height="320px"></video>

#   <label>Output OpenCV</label>
#   <canvas id="canvas-output" width="480px" height="320px"></canvas>
#   <script src="../javascript/opencv.js"></script>
#   <p> oiiii </p>
# '''

# components.html(html_string)
# components.iframe('https://docs.streamlit.io/en/latest', width=800, height=600)

from streamlit_webrtc import webrtc_streamer
# import av


# class VideoProcessor:

#     def recv(self, frame):
#         img = frame.to_ndarray(format="bgr24")

#         flipped = img[::-1, :, :]

#         return av.VideoFrame.from_ndarray(flipped, format="bgr24")


webrtc_streamer(key="example")
