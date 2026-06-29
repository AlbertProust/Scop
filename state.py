"""Shared scene state for the OBJ viewer."""

window = None

cameraX = 0.0
cameraY = 0.0
cameraZ = 5.0

targetX = 0.0
targetY = 0.0
targetZ = 0.0

cameraDistance = 5.0
cameraYaw = 0.0
cameraPitch = 0.0
obj_radius = 1.0

texture_id = None
texture_used = False
texture_coords = []
transition_active = False
transition_value = 0.0
transition_start = 0.0
transition_duration = 1.0
face_texcoords = []
vertices = []
indices = []
faces = []
colors = []
