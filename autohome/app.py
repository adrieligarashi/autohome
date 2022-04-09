# Core Pkgs
import streamlit as st

# Utils Pkgs
import codecs

# Components Pkgs
import streamlit.components.v1 as stc


# Custom Components Fxn
def st_calculator(calc_html, width=700, height=500):
    calc_file = codecs.open(calc_html, 'r')
    page = calc_file.read()
    stc.html(page, width=width, height=height, scrolling=False)


def main():
    """A Calculator App with Streamlit Components"""


    st.subheader("Advanced Calculator")
    # components.html(html_temp)
    st_calculator('index.html')
    st.subheader("AAAAAA")



if __name__ == '__main__':
    main()



#######################

# import cv2
# import streamlit as st

# st.title("Webcam Application")
# run = st.checkbox('Run')
# FRAME_WINDOW = st.image([])
# cam = cv2.VideoCapture(-1)

# while run:
#     ret, frame = cam.read()
#     # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     FRAME_WINDOW.image(frame)
# else:
#     st.write('Stopped')
