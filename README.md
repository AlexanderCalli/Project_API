# ComfyUI Image Generation API

This project provides a Flask-based API for generating images using ComfyUI, storing them in Supabase, and sending real-time updates to clients using Server-Sent Events (SSE).

## Features

- Image generation using ComfyUI
- Real-time progress updates via SSE
- Image storage in Supabase
- Metadata storage in Supabase database

## Main Components

### 1. Flask API (`generate_image` function)

- Handles POST requests to `/generate`
- Processes user inputs for image generation
- Manages the image generation process
- Sends real-time updates to the client
- Stores generated images and metadata

### 2. Image Generation (`get_images` function)

- Connects to ComfyUI WebSocket server
- Sends the workflow for image generation
- Monitors the generation process
- Sends updates every second during generation

### 3. Supabase Integration

- Stores generated images in Supabase storage
- Saves image metadata in Supabase database

## Workflow

1. Client sends a POST request to `/generate` with image generation parameters.
2. The server starts the image generation process in a separate thread.
3. Real-time updates are sent to the client every second during generation.
4. Generated images are processed, stored in Supabase, and metadata is saved.
5. A final update with results is sent to the client.

## Key Functions

- `generate_image()`: Main API endpoint handler
- `get_images()`: Manages the ComfyUI image generation process
- `queue_prompt()`: Sends the workflow to ComfyUI
- `get_image()`: Retrieves generated images from ComfyUI
- `get_history()`: Fetches generation history from ComfyUI

## Environment Setup

The application requires the following environment variables:

- `SUPABASE_URL`: URL of your Supabase project
- `SUPABASE_KEY`: API key for Supabase

## Dependencies

- Flask
- Supabase Python client
- websocket-client
- Pillow (PIL)
- python-dotenv

## Usage

1. Set up the required environment variables.
2. Start the Flask server.
3. Send a POST request to `/generate` with the desired image generation parameters.
4. Listen for SSE updates to track the generation progress.
5. Receive the final results with links to the generated images.

## Note

This application is designed to work with a running ComfyUI instance. Make sure ComfyUI is properly set up and running before using this API.