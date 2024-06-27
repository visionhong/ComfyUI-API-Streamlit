import streamlit as st
from streamlit_image_comparison import image_comparison


@st.experimental_dialog("Generated Image", width="large")
def comparer(t2i_image, i2i_image):
    image_comparison(
        img1=t2i_image,
        img2=i2i_image,
        label1="t2i",
        label2="i2i",
        starting_position=50,
        show_labels=True,
        make_responsive=False,
        in_memory=True,
    )