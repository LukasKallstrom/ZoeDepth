import open3d as o3d
import numpy as np
from pymongo import MongoClient
import gridfs

# Connect to MongoDB
client = MongoClient("mongodb+srv://kallstrom00:Lukasamigo123@cluster0.og45btg.mongodb.net/")
db = client['image_mesh_db']
collection = db['image_mesh_metadata']
fs = gridfs.GridFS(db)

# Retrieve the metadata document (assuming you want to retrieve the most recent one)
metadata = collection.find_one(sort=[("created_at", -1)])

# Check if metadata is retrieved
if metadata:
    # Retrieve vertices and triangles data from GridFS
    vertices_data = fs.get(metadata['vertices_id']).read()
    triangles_data = fs.get(metadata['triangles_id']).read()
    
    # Convert data back to numpy arrays
    vertices = np.frombuffer(vertices_data, dtype=np.float64).reshape(-1, 3)
    triangles = np.frombuffer(triangles_data, dtype=np.int32).reshape(-1, 3)
    
    # Create an open3d TriangleMesh object
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(triangles)

    # Compute vertex normals
    mesh.compute_vertex_normals()

    # Visualize the mesh
    o3d.visualization.draw_geometries([mesh])
else:
    print("No metadata found in the database.")
