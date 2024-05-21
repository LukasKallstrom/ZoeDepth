import torch
import PIL.Image as Image
import open3d as o3d
import numpy as np
from datetime import datetime
from pymongo import MongoClient
import gridfs
from bson import ObjectId
from .gradio_im_to_3d import get_mesh

# Check if CUDA is available and set device accordingly
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load the pretrained model
model = torch.hub.load('isl-org/ZoeDepth', "ZoeD_N", pretrained=True).to(DEVICE).eval()

# Load the image
image_path = "C://Users//kalls//Documents//GitHub//ZoeDepth//ui//IMG_1877.jpg"
image = Image.open(image_path)

# Generate the mesh from the image
mesh_path = get_mesh(model, image, keep_edges=False)

# Load the GLB mesh file using open3d
loaded_mesh = o3d.io.read_triangle_mesh(mesh_path)

# Extract mesh data (vertices and faces)
vertices = np.asarray(loaded_mesh.vertices).tolist()
triangles = np.asarray(loaded_mesh.triangles).tolist()

# Visualize the mesh
o3d.visualization.draw_geometries([loaded_mesh])

# Connect to MongoDB
client = MongoClient("mongodb+srv://kallstrom00:Lukasamigo123@cluster0.og45btg.mongodb.net/")
db = client['image_mesh_db']
collection = db['image_mesh_metadata']

# Use GridFS to store large mesh data
fs = gridfs.GridFS(db)

# Convert mesh data to bytes and store in GridFS
vertices_id = fs.put(np.array(vertices).tobytes(), encoding='utf-8')
triangles_id = fs.put(np.array(triangles).tobytes(), encoding='utf-8')

# Prepare metadata document with mesh data stored in GridFS
metadata = {
    "image_path": image_path,
    "mesh_path": mesh_path,
    "created_at": datetime.now(),
    "device": DEVICE,
    "vertices_id": vertices_id,
    "triangles_id": triangles_id
}

# Insert metadata into MongoDB
collection.insert_one(metadata)

print(f"Metadata and mesh data for {image_path} inserted into MongoDB.")
