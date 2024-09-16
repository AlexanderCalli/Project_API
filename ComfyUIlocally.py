from flask import Flask, request, jsonify
import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import websocket
import uuid
import urllib.request
import urllib.parse
from datetime import datetime
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

# Load the workflow JSON
with open('workflow_fluxdev1_16_api.json', 'r') as f:
    workflow = json.load(f)

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break  # Execution is done
        else:
            continue  # previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
        output_images[node_id] = images_output

    return output_images

@app.route('/generate', methods=['POST'])
def generate_image():
    # Get data from the request
    data = request.json

    # Update the workflow with user inputs
    workflow["6"]["inputs"]["text"] = data.get('prompt', "Default prompt")
    workflow["27"]["inputs"]["width"] = data.get('width', 832)
    workflow["27"]["inputs"]["height"] = data.get('height', 1216)
    workflow["17"]["inputs"]["steps"] = data.get('steps', 20)
    workflow["26"]["inputs"]["guidance"] = data.get('guidance', 3.5)
    workflow["25"]["inputs"]["noise_seed"] = data.get('seed', 296679418561412)

    # Generate the image
    ws = websocket.WebSocket()
    ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
    images = get_images(ws, workflow)

    results = []

    for node_id in images:
        for i, image_data in enumerate(images[node_id]):
            image = Image.open(io.BytesIO(image_data))
            
            # Generate filename with current date and time
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Output_{current_time}_{i}.png"
            
            # Upload image to Supabase Storage
            storage_path = f"generated_images/{filename}"
            supabase.storage.from_("images").upload(storage_path, image_data)
            
            # Insert metadata into the database
            image_metadata = {
                "filename": filename,
                "prompt": workflow["6"]["inputs"]["text"],
                "storage_path": storage_path,
                "width": image.width,
                "height": image.height
            }
            result = supabase.table("generated_images").insert(image_metadata).execute()
            
            # Get the public URL of the uploaded image
            public_url = supabase.storage.from_("images").get_public_url(storage_path)
            
            results.append({
                "filename": filename,
                "storage_path": storage_path,
                "public_url": public_url,
                "width": image.width,
                "height": image.height
            })

    return jsonify({
        "message": "Images generated and stored successfully",
        "results": results
    })

if __name__ == '__main__':
    app.run(debug=True)