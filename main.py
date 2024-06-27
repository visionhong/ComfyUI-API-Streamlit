import streamlit as st
import argparse

from utils.api_formatter import request_inference
from utils.util import  delete_queue, image_thumbnail
from utils.dialog import comparer


def side_bar():
    with st.sidebar:    
        st.markdown("# Configuration")
        st.number_input("ImgNum", min_value=1, max_value=4, value=2, key="batch_size", help="num of generate images")
        st.number_input("Seed", min_value=1, max_value=4294967295, value=42, key="seed", help="randomness")

        st.session_state["current_prompt"] = st.text_area("prompt", value="", height=130)
        st.write("")
        col1, col2 = st.columns((1, 1))

        if col1.button("Stop", key="stop", use_container_width=True, help="If you're not happy with the generated design draft, hit the button and generate it again!"):
            if "server_address" in st.session_state and "client_id" in st.session_state:
                delete_queue(st.session_state["server_address"], st.session_state["client_id"])


    if col2.button("**Generate**", key="gen", type="primary", use_container_width=True):

        prompt = st.session_state["current_prompt"]
        st.session_state["prompt"] = prompt

        with st.spinner("working on progress.."):
            request_inference(server_address = st.session_state["server_address"],
                            prompt = st.session_state["prompt"],
                            batch_size = st.session_state["batch_size"],
                            seed = st.session_state['seed'])
                
def main():
    st.set_page_config(layout="centered")
    
    st.session_state["server_address"] = args.server_address
    st.markdown("### 🎨 Labs")
    # if "server_address" in st.session_state and "client_id" in st.session_state:
    #     delete_queue(st.session_state["server_address"], st.session_state["client_id"])

    if "i2i" in st.session_state:
        for i in range(0, len(st.session_state["i2i"]), 2):
                cols = st.columns(2)

                for j in range(2):
                    if i + j < len(st.session_state["i2i"]):
                    
                        image = image_thumbnail(st.session_state["i2i"][i + j])
                        cols[j].image(image)

                        _, edit_col, _ = cols[j].columns((1, 2, 1))
                        
                        if edit_col.button(f'Comparer', key=str(i+j+1), use_container_width=True):
                                comparer(t2i_image=st.session_state["t2i"][i + j],
                                         i2i_image=st.session_state["i2i"][i + j]
                                    )

    side_bar()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process server address.')
    parser.add_argument('--server_address', type=str, required=True, help='The address of the server. ex) 12.34.56.78:8188')

    args = parser.parse_args()
    main()
