import plotly.graph_objects as go
import numpy as np
import pyodide # type: ignore

# --- 1. Primitive Generation Functions ---

def create_cube_mesh(center=[0,0,0], size=[1,1,1]):
    """
    Creates vertices and faces for a cube.
    Returns x, y, z coordinates and i, j, k indices for faces.
    """
    x, y, z = center[0], center[1], center[2]
    sx, sy, sz = size[0]/2, size[1]/2, size[2]/2

    # Vertices of the cube
    v = np.array([
        [x - sx, y - sy, z - sz], # 0
        [x + sx, y - sy, z - sz], # 1
        [x + sx, y + sy, z - sz], # 2
        [x - sx, y + sy, z - sz], # 3
        [x - sx, y - sy, z + sz], # 4
        [x + sx, y - sy, z + sz], # 5
        [x + sx, y + sy, z + sz], # 6
        [x - sx, y + sy, z + sz]  # 7
    ])

    # Define faces using vertex indices (two triangles per face)
    faces = np.array([
        # Bottom
        [0, 1, 2], [0, 2, 3],
        # Top
        [4, 5, 6], [4, 6, 7],
        # Front
        [0, 1, 5], [0, 5, 4],
        # Back
        [3, 2, 6], [3, 6, 7],
        # Left
        [0, 3, 7], [0, 7, 4],
        # Right
        [1, 2, 6], [1, 6, 5]
    ])

    return v, faces # Return vertices as a single array for easier transformation

def create_cylinder_mesh(center=[0,0,0], radius=0.5, height=1, segments=20):
    """
    Creates vertices and faces for a cylinder.
    Returns vertices array and i, j, k indices for faces.
    """
    theta = np.linspace(0, 2*np.pi, segments, endpoint=False)
    x_circle = radius * np.cos(theta)
    y_circle = radius * np.sin(theta)

    # Bottom circle vertices
    v_bottom = np.column_stack([x_circle + center[0], y_circle + center[1], np.full(segments, center[2] - height/2)])
    # Top circle vertices
    v_top = np.column_stack([x_circle + center[0], y_circle + center[1], np.full(segments, center[2] + height/2)])

    # Center points for caps
    v_center_bottom = np.array([[center[0], center[1], center[2] - height/2]])
    v_center_top = np.array([[center[0], center[1], center[2] + height/2]])

    # Combine all vertices
    vertices = np.vstack([v_bottom, v_top, v_center_bottom, v_center_top])

    # Indices for caps
    idx_center_bottom = 2 * segments
    idx_center_top = 2 * segments + 1

    faces = []
    # Bottom cap
    for i in range(segments):
        faces.append([i, (i + 1) % segments, idx_center_bottom])
    # Top cap
    for i in range(segments):
        faces.append([segments + i, segments + (i + 1) % segments, idx_center_top])

    # Side faces
    for i in range(segments):
        v0 = i
        v1 = (i + 1) % segments
        v2 = segments + (i + 1) % segments
        v3 = segments + i
        faces.append([v0, v1, v2]) # Triangle 1
        faces.append([v0, v2, v3]) # Triangle 2

    return vertices, np.array(faces)


def create_cone_mesh(center=[0,0,0], radius=0.5, height=1, segments=20):
    """
    Creates vertices and faces for a cone.
    Returns vertices array and i, j, k indices for faces.
    """
    theta = np.linspace(0, 2*np.pi, segments, endpoint=False)
    x_circle = radius * np.cos(theta)
    y_circle = radius * np.sin(theta)

    # Base circle vertices
    v_base = np.column_stack([x_circle + center[0], y_circle + center[1], np.full(segments, center[2])])
    # Apex vertex
    v_apex = np.array([[center[0], center[1], center[2] + height]])
    # Center point for base cap
    v_center_base = np.array([[center[0], center[1], center[2]]])

    # Combine all vertices
    vertices = np.vstack([v_base, v_apex, v_center_base])

    idx_apex = segments
    idx_center_base = segments + 1

    faces = []
    # Side faces
    for i in range(segments):
        v0 = i
        v1 = (i + 1) % segments
        faces.append([v0, v1, idx_apex])
    # Base cap
    for i in range(segments):
        faces.append([i, (i + 1) % segments, idx_center_base])

    return vertices, np.array(faces)

def create_torus_mesh(center=[0,0,0], major_radius=1.0, minor_radius=0.2, major_segments=30, minor_segments=15):
    """
    Creates vertices and faces for a torus.
    Returns vertices array and i, j, k indices for faces.
    """
    vertices = []
    faces = []

    for i in range(major_segments):
        phi = 2 * np.pi * i / major_segments
        for j in range(minor_segments):
            theta = 2 * np.pi * j / minor_segments

            x = (major_radius + minor_radius * np.cos(theta)) * np.cos(phi) + center[0]
            y = (major_radius + minor_radius * np.cos(theta)) * np.sin(phi) + center[1]
            z = minor_radius * np.sin(theta) + center[2]
            vertices.append([x, y, z])

    # Generate faces
    for i in range(major_segments):
        for j in range(minor_segments):
            v0 = i * minor_segments + j
            v1 = (i * minor_segments + (j + 1) % minor_segments)
            v2 = ((i + 1) % major_segments * minor_segments + (j + 1) % minor_segments)
            v3 = ((i + 1) % major_segments * minor_segments + j)

            faces.append([v0, v1, v2])
            faces.append([v0, v2, v3])

    return np.array(vertices), np.array(faces)


# --- 2. Transformation Functions ---

def translate(vertices, tx, ty, tz):
    """Translates vertices by (tx, ty, tz)."""
    return vertices + np.array([tx, ty, tz])

def rotate_x(vertices, angle_deg):
    """Rotates vertices around the X-axis."""
    angle_rad = np.deg2rad(angle_deg)
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(angle_rad), -np.sin(angle_rad)],
        [0, np.sin(angle_rad), np.cos(angle_rad)]
    ])
    return vertices @ Rx.T

def rotate_y(vertices, angle_deg):
    """Rotates vertices around the Y-axis."""
    angle_rad = np.deg2rad(angle_deg)
    Ry = np.array([
        [np.cos(angle_rad), 0, np.sin(angle_rad)],
        [0, 1, 0],
        [-np.sin(angle_rad), 0, np.cos(angle_rad)]
    ])
    return vertices @ Ry.T

def rotate_z(vertices, angle_deg):
    """Rotates vertices around the Z-axis."""
    angle_rad = np.deg2rad(angle_deg)
    Rz = np.array([
        [np.cos(angle_rad), -np.sin(angle_rad), 0],
        [np.sin(angle_rad), np.cos(angle_rad), 0],
        [0, 0, 1]
    ])
    return vertices @ Rz.T

def scale(vertices, sx, sy, sz):
    """Scales vertices by (sx, sy, sz)."""
    return vertices * np.array([sx, sy, sz])

# --- 3. Scene Graph Definition for Rocket ---

scene_graph = {
    "rocket": {
        "type": "group",
        "children": [
            {
                "name": "body",
                "type": "primitive",
                "shape": "cylinder",
                "color": "silver",
                "initial_radius": 1.0,
                "initial_height": 6.0,
                "transformations": [
                    {"type": "translate", "params": [0, 0, 3.0]} # Center the body around Z=3.0 (half its height)
                ]
            },
            {
                "name": "nose_cone",
                "type": "primitive",
                "shape": "cone",
                "color": "red",
                "initial_radius": 1.0,
                "initial_height": 3.0,
                "transformations": [
                    {"type": "translate", "params": [0, 0, 6.0]} # Place on top of the body (body height + cone base at body top)
                ]
            },
            # Fins (3x)
            {
                "name": "fin_1",
                "type": "primitive",
                "shape": "cube", # Using cube for fin base, will be scaled/translated
                "color": "blue",
                "initial_size": [0.2, 2.5, 2.0], # Thin, wide, tall
                "transformations": [
                    {"type": "translate", "params": [0, -1.0, 1.0]}, # Position relative to body base
                    {"type": "rotate_z", "params": [0]},
                    {"type": "rotate_x", "params": [10]} # Slight angle for aesthetic
                ]
            },
            {
                "name": "fin_2",
                "type": "primitive",
                "shape": "cube",
                "color": "blue",
                "initial_size": [0.2, 2.5, 2.0],
                "transformations": [
                    {"type": "translate", "params": [0, -1.0, 1.0]},
                    {"type": "rotate_z", "params": [120]}, # Rotate around Z for placement
                    {"type": "rotate_x", "params": [10]}
                ]
            },
            {
                "name": "fin_3",
                "type": "primitive",
                "shape": "cube",
                "color": "blue",
                "initial_size": [0.2, 2.5, 2.0],
                "transformations": [
                    {"type": "translate", "params": [0, -1.0, 1.0]},
                    {"type": "rotate_z", "params": [240]}, # Rotate around Z for placement
                    {"type": "rotate_x", "params": [10]}
                ]
            },
            # Windows (Multiple spheres)
            {
                "name": "window_1",
                "type": "primitive",
                "shape": "sphere", # We'll create a sphere mesh function
                "color": "lightblue",
                "initial_radius": 0.3,
                "transformations": [
                    {"type": "translate", "params": [0.8, 0, 5.0]} # On the body, higher up
                ]
            },
            {
                "name": "window_2",
                "type": "primitive",
                "shape": "sphere",
                "color": "lightblue",
                "initial_radius": 0.3,
                "transformations": [
                    {"type": "translate", "params": [0.8 * np.cos(np.deg2rad(90)), 0.8 * np.sin(np.deg2rad(90)), 4.0]}, # Rotated around body
                    {"type": "rotate_z", "params": [90]} # For visualization, just translate
                ]
            },
             {
                "name": "window_3",
                "type": "primitive",
                "shape": "sphere",
                "color": "lightblue",
                "initial_radius": 0.3,
                "transformations": [
                    {"type": "translate", "params": [0.8 * np.cos(np.deg2rad(180)), 0.8 * np.sin(np.deg2rad(180)), 5.0]}, # Rotated around body
                    {"type": "rotate_z", "params": [180]}
                ]
            },
            # Engine Exhaust (Smaller cylinder at the bottom)
            {
                "name": "exhaust",
                "type": "primitive",
                "shape": "cylinder",
                "color": "darkgrey",
                "initial_radius": 0.7,
                "initial_height": 1.0,
                "transformations": [
                    {"type": "translate", "params": [0, 0, -0.5]} # Below the body base
                ]
            },
            # Engine Nozzles (Smaller cones inside the exhaust)
            {
                "name": "nozzle_1",
                "type": "primitive",
                "shape": "cone",
                "color": "orange",
                "initial_radius": 0.3,
                "initial_height": 0.8,
                "transformations": [
                    {"type": "translate", "params": [0.3, 0.3, -0.9]}, # Inside exhaust, slightly offset
                    {"type": "rotate_x", "params": [180]} # Pointing downwards
                ]
            },
             {
                "name": "nozzle_2",
                "type": "primitive",
                "shape": "cone",
                "color": "orange",
                "initial_radius": 0.3,
                "initial_height": 0.8,
                "transformations": [
                    {"type": "translate", "params": [-0.3, -0.3, -0.9]},
                    {"type": "rotate_x", "params": [180]}
                ]
            },
            # Decorative Rings (Torus)
            {
                "name": "ring_top",
                "type": "primitive",
                "shape": "torus", # We'll create a torus mesh function
                "color": "gold",
                "initial_major_radius": 1.1, # Slightly larger than body radius
                "initial_minor_radius": 0.05,
                "transformations": [
                    {"type": "translate", "params": [0, 0, 5.5]}, # Near the nose cone joint
                ]
            },
            {
                "name": "ring_bottom",
                "type": "primitive",
                "shape": "torus",
                "color": "gold",
                "initial_major_radius": 1.1,
                "initial_minor_radius": 0.05,
                "transformations": [
                    {"type": "translate", "params": [0, 0, 1.5]}, # Lower part of the body
                ]
            }
        ]
    }
}

# Add create_sphere_mesh for windows
def create_sphere_mesh(center=[0,0,0], radius=0.5, segments=20):
    """
    Creates vertices and faces for a sphere using spherical coordinates.
    Returns vertices array and i, j, k indices for faces.
    """
    vertices = []
    faces = []

    # Generate vertices
    for i in range(segments + 1):
        lat = np.pi * (-0.5 + i / segments) # Latitude from -pi/2 to pi/2
        for j in range(segments + 1):
            lon = 2 * np.pi * j / segments # Longitude from 0 to 2pi

            x = radius * np.cos(lat) * np.cos(lon) + center[0]
            y = radius * np.cos(lat) * np.sin(lon) + center[1]
            z = radius * np.sin(lat) + center[2]
            vertices.append([x, y, z])

    # Generate faces (quads, then split into triangles)
    for i in range(segments):
        for j in range(segments):
            v0 = i * (segments + 1) + j
            v1 = v0 + 1
            v2 = (i + 1) * (segments + 1) + j + 1
            v3 = (i + 1) * (segments + 1) + j

            # Ensure faces are correctly oriented (counter-clockwise)
            faces.append([v0, v1, v2]) # Triangle 1
            faces.append([v0, v2, v3]) # Triangle 2
            
    return np.array(vertices), np.array(faces)

# --- 4. Scene Traversal and Plotly Generation ---

def build_scene(scene_graph_node):
    """
    Recursively builds the 3D scene from the scene graph, applying transformations.
    Returns a list of Plotly Mesh3d traces.
    """
    traces = []
    
    if scene_graph_node["type"] == "primitive":
        shape = scene_graph_node["shape"]
        color = scene_graph_node["color"]
        
        # Get initial vertices and faces based on shape
        if shape == "cube":
            vertices, faces = create_cube_mesh(size=scene_graph_node["initial_size"])
        elif shape == "cylinder":
            vertices, faces = create_cylinder_mesh(radius=scene_graph_node["initial_radius"], 
                                                     height=scene_graph_node["initial_height"])
        elif shape == "cone":
            vertices, faces = create_cone_mesh(radius=scene_graph_node["initial_radius"],
                                                height=scene_graph_node["initial_height"])
        elif shape == "sphere":
            vertices, faces = create_sphere_mesh(radius=scene_graph_node["initial_radius"])
        elif shape == "torus":
             vertices, faces = create_torus_mesh(major_radius=scene_graph_node["initial_major_radius"],
                                                 minor_radius=scene_graph_node["initial_minor_radius"])
        else:
            raise ValueError(f"Unknown primitive shape: {shape}")
        
        # Apply local transformations
        for transform_info in scene_graph_node["transformations"]:
            t_type = transform_info["type"]
            t_params = transform_info["params"]
            
            if t_type == "translate":
                vertices = translate(vertices, *t_params)
            elif t_type == "rotate_x":
                vertices = rotate_x(vertices, *t_params)
            elif t_type == "rotate_y":
                vertices = rotate_y(vertices, *t_params)
            elif t_type == "rotate_z":
                vertices = rotate_z(vertices, *t_params)
            elif t_type == "scale":
                # For scaling, we apply it directly to the vertices
                # Note: Scaling combined with translation needs careful order
                vertices = scale(vertices, *t_params)
            else:
                print(f"Warning: Unknown transformation type: {t_type}")
        
        traces.append(go.Mesh3d(
            x=vertices[:,0], y=vertices[:,1], z=vertices[:,2],
            i=faces[:,0], j=faces[:,1], k=faces[:,2],
            color=color,
            opacity=1.0, # Make rocket parts fully opaque
            flatshading=True # For a more "faceted" look, common for toy models
        ))
        
    elif scene_graph_node["type"] == "group":
        for child_node in scene_graph_node["children"]:
            traces.extend(build_scene(child_node)) # No parent_transform needed here as transforms are absolute
            
    return traces

# Create the Plotly figure
def create_rocket_figure():
    traces = build_scene(scene_graph["rocket"])
    
    fig = go.Figure(data=traces)

    fig.update_layout(
        title='3D Rocket Model',
        scene=dict(
            xaxis=dict(showbackground=False, showticklabels=False, zeroline=False, visible=False),
            yaxis=dict(showbackground=False, showticklabels=False, zeroline=False, visible=False),
            zaxis=dict(showbackground=False, showticklabels=False, zeroline=False, visible=False),
            aspectmode='data', # Ensures equal scaling across axes
            camera=dict(
                eye=dict(x=1.8, y=1.8, z=1.0), # Camera position, looking slightly down at the rocket
                center=dict(x=0, y=0, z=3.0), # Center of the rocket
                up=dict(x=0, y=0, z=1)  # Z-axis is up
            ),
            # Optional: Add grid and axis labels if you want to see the coordinates
            # xaxis_title='X',
            # yaxis_title='Y',
            # zaxis_title='Z',
            # showgrid=True,
            # gridcolor='lightgray',
            # showticklabels=True
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        paper_bgcolor='rgba(0,0,0,0)', # Transparent background
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# Main execution block for Pyodide
if __name__ == "__main__":
    fig = create_rocket_figure()
    # Serialize the figure to JSON and pass it to JavaScript
    pyodide.webloop.run_until_complete(pyodide.eval(f"""
        (() => {{
            const fig = JSON.parse('{fig.to_json()}');
            Plotly.newPlot('plotly-div', fig.data, fig.layout);
        }})()
    """))