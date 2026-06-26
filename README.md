*This project has been created as part of the 42 curriculum by Aproust*

# Description

This project is a simple 3D OBJ viewer built with GLFW for window handling and OpenGL for rendering. It loads Wavefront OBJ models, applies BMP textures, and lets the user rotate, zoom, and move the camera around the object.

# Instructions

1. Install the required Python packages if not already installed:

```bash
pip install glfw PyOpenGL
```

2. Run the viewer from the project root with an OBJ file and optional BMP texture:

```bash
python3 -m final_scop path/to/model.obj [path/to/texture.bmp]
```

3. Use the controls shown in the terminal:

- Rotation: `W`, `S`, `A`, `D` or arrow keys
- Zoom: `Q` (back), `E` (forward)
- Move center: `I`, `K`, `J`, `L`
- Quit: `ESC`
