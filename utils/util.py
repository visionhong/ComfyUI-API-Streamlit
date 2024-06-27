import json
import urllib.request
import urllib.parse

import numpy as np
import cv2
import streamlit as st
from PIL import Image


@st.cache_data  
def image_thumbnail(array, max_width=800, max_height=600):
    image = Image.fromarray(array.astype('uint8'))
    # 이미지의 크기를 조절
    image.thumbnail((max_width, max_height), Image.LANCZOS)
    return image


def get_node_by_title(prompt_workflow, title):
    # find node by title (case-insensitive)
    lower_title = title.lower()
    node_list = []
    for id in prompt_workflow:
        node = prompt_workflow[id]
        node_title = node["_meta"]["title"].lower()  
        if node_title == lower_title:
            node_list.append(id)
    return node_list


def get_node_by_class_type(prompt_workflow, class_type):
    # find node by title (case-insensitive)
    lower_class_type = class_type.lower()
    node_list = []
    for id in prompt_workflow:
        node = prompt_workflow[id]
        node_class_type = node["class_type"].lower()  
        if node_class_type == lower_class_type:
            node_list.append(id)
    return node_list

    
def update_workflow(workflow, prompt, seed, batch_size):
    
    sampler_ids = get_node_by_title(workflow, 'KSampler')
    for id in sampler_ids:
        workflow[id]["inputs"]["seed"] = seed

    empty_latent_ids = get_node_by_title(workflow, 'Empty Latent Image')
    for id in empty_latent_ids:
        workflow[id]["inputs"]["batch_size"] = batch_size

    clip_ids = get_node_by_class_type(workflow, 'CLIPTextEncode')
    for id in clip_ids:
        if workflow[id]["_meta"]["title"] == "positive_prompt":
            workflow[id]["inputs"]["text"] = "zavy-ctflt, drawing, " + prompt  # zavy-ctflt, drawing -> lora trigger words
    
    preview_ids = get_node_by_class_type(workflow, 'PreviewImage')
    for id in preview_ids:
        workflow[id]["_meta"]["title"] = "Send Image (WebSocket)"
        workflow[id]["class_type"] = "ETN_SendImageWebSocket"

    return workflow
   
def queue_workflow(workflow, server_address, client_id):
    p = {"prompt": workflow, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')  # encode json to bytes
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_queue(server_address):
    # create the GET request
    req = urllib.request.Request(f"http://{server_address}/queue", method='GET')

    # sending the request and getting the response
    with urllib.request.urlopen(req) as response:
        response_data = json.loads(response.read().decode('utf-8'))

        return response_data

def cancel_running(server_address):
    url = f"http://{server_address}/interrupt"
    req_headers = {'Content-Type': 'application/json'}    
    interrupt_request = urllib.request.Request(url, headers=req_headers, method='POST')

    # send request and get the response
    with urllib.request.urlopen(interrupt_request) as response:
        return response
    
def delete_queue(server_address, client_id):
    response = get_queue(server_address)
    try:
        task = response["queue_running"][0]
        if task[-2]["client_id"] == client_id:
            cancel_running(server_address)

    except:
        pass
        # st.toast("No queue")
   

def receive_images(ws, prompt_id, image_queue, progress_queue, batch_size):
    image_batch = []
    cnt = 0
    while True:
        out = ws.recv()  # Receive WS message
        if isinstance(out, str):
            message = json.loads(out)
    
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break  # Exit the loop as the execution is complete.
            elif message['type'] == 'progress':
                data = message['data']
                if int(data['max']) == 1:  # except invert image node
                    continue

                progress_value = data['value'] / data['max']
                progress_queue.put(progress_value)

        else:  # binary image data        
            image_data = np.frombuffer(out[8:], dtype=np.uint8)
            image_array_bgr = cv2.imdecode(image_data, cv2.IMREAD_COLOR)            
            image = cv2.cvtColor(image_array_bgr, cv2.COLOR_BGR2RGB)

            image_batch.append(image)
            if len(image_batch) == batch_size:
                cnt +=1
                image_queue.put(image_batch)
                image_batch = []

