import streamlit as st
import websocket
import json
import uuid
import threading
import queue

from utils.util import update_workflow, queue_workflow, receive_images, image_thumbnail


def request_inference(server_address, prompt, batch_size, seed):
    client_id = str(uuid.uuid4())  # generate unique id
    st.session_state["client_id"] = client_id
    
    with open("workflows/workflow_api.json", "r", encoding="utf-8") as f:
        workflow_jsondata = f.read()

    workflow = json.loads(workflow_jsondata)
    new_workflow = update_workflow(workflow, prompt, seed, batch_size)  # update workflow
   
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    
    prompt_id = queue_workflow(new_workflow, server_address, client_id)['prompt_id']
    image_queue = queue.Queue()
    progress_queue = queue.Queue()

    # Start a thread to receive images
    thread = threading.Thread(target=receive_images, args=(ws, prompt_id, image_queue, progress_queue, batch_size))
    thread.start()
    
    progress_bar = st.sidebar.progress(0, "Initializing...")
    
    cnt = 0
    cols1 = st.columns((1, 1))
    cols2 = st.columns((1, 1))

    image_placeholders = [
        [cols1[0].empty(), cols1[1].empty()],
        [cols2[0].empty(), cols2[1].empty()]
    ]
    
    progress_text_list = ["Text to Image..", "Image to Image.."]
    img_list = []
    while thread.is_alive() or not image_queue.empty() or not progress_queue.empty():
        while not progress_queue.empty():
            progress_value = progress_queue.get()
            progress_bar.progress(progress_value, text=progress_text_list[cnt])

        while not image_queue.empty():
            image = image_queue.get()
            for i in range(len(image)):
                row = i // 2
                col = i % 2
                if row < 2 and col < 2:
                    img = image_thumbnail(image[i])
                    image_placeholders[row][col].image(img)
            img_list.append(image)
            cnt += 1

    # Ensure the thread has completed
    thread.join()
    
    if len(img_list) == 2:
        st.session_state["t2i"] = img_list[0]
        st.session_state["i2i"] = img_list[1]

    progress_bar.progress(100, text="Complete!")

    st.rerun()
