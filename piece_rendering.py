#To be called with 
# 'blender --background --python piece_rendering.py'
# will render all pieces in separate files

import bpy
import os
import sys       # to get command line args
import argparse  # to parse options for us and print a nice help message
import math
import piece
import solve
import numpy as np


def color(r, g, b):
    return (r/255, g/255, b/255, 1)


def get_piece_colors(piece):
    p_idx = int(piece.name[1])
    cube_colors = []
    beam_colors = []
    cube_colors.append(color(68, 168, 52))
    beam_colors.append(color(146, 214, 135))

    cube_colors.append(color(168, 80, 72))
    beam_colors.append(color(235, 142, 134))

    cube_colors.append(color(194, 121, 25))
    beam_colors.append(color(247, 182, 96))

    cube_colors.append(color(237, 240, 53))
    beam_colors.append(color(240, 242, 124))

    cube_colors.append(color(42, 99, 245))
    beam_colors.append(color(126, 157, 237))

    cube_colors.append(color(175, 74, 245))
    beam_colors.append(color(209, 142, 250))

    cube_colors.append(color(245, 76, 217))
    beam_colors.append(color(247, 142, 230))

    cube_colors.append(color(137, 89, 189))
    beam_colors.append(color(176, 136, 219))
    return (cube_colors[p_idx], beam_colors[p_idx])


def render_state(puzzle, suffix):
    save_blend = True
    filepath = os.getcwd()
    png_filename = f"{filepath}/puzzle_state{suffix:02d}.png"
    blend_filename = f"{filepath}/puzzle_state{suffix:02d}.blend"

    # Clear existing objects.
    bpy.ops.wm.read_factory_settings(use_empty=True)

    scene = bpy.context.scene

    #set transparent background
    scene.render.film_transparent = True


    size = 0.2
    coord = 2*size
    i = 0
    for p in puzzle:
        p_idx = int(p.name[1]) - 1
        cubecolor, beamcolor = get_piece_colors(p)
        mat = bpy.data.materials.new("cubecolor")
        mat.diffuse_color = cubecolor
        for block in p.blocks:
            c = block.pos
            bpy.ops.mesh.primitive_cube_add()
            cube = bpy.context.selected_objects[0]
            cube.name = f"cube{i}"
            cube.location=(coord*c.x, coord*c.y, coord*c.z)
            bpy.ops.transform.resize(value = (size, size, size))
            cube.color = cubecolor
            cube.active_material = mat
            i += 1

        i = 0
        sizeb=0.2
        coordb = 2*sizeb
        mat2 = bpy.data.materials.new("beamcolor")
        mat2.diffuse_color = beamcolor
        for beam in p.beams:
            for block in beam:
                c = block.pos
                bpy.ops.mesh.primitive_cube_add()
                cube2 = bpy.context.selected_objects[0]
                cube2.name = f"beam{i}"
                cube2.location = (coordb*c.x, coordb*c.y, coordb*c.z)
                bpy.ops.transform.resize(value = (sizeb, sizeb, sizeb))
                cube2.color = beamcolor
                cube2.active_material = mat2
                i += 1

    # Camera
    cam_data = bpy.data.cameras.new("MyCam")
    cam_ob = bpy.data.objects.new(name="MyCam", object_data=cam_data)
    scene.collection.objects.link(cam_ob)  # instance the camera object in the scene
    scene.camera = cam_ob       # set the active camera

    pi = math.pi;
    cam_ob.rotation_mode = 'XYZ'
    cam_ob.location = -2.1356, -4.0859, 10.078
    cam_ob.rotation_euler = 64.5*pi/180, -2.9*pi/180, -397*pi/180

    # Light
    light_data = bpy.data.lights.new("MyLight", 'POINT')
    light_ob = bpy.data.objects.new(name="MyLight", object_data=light_data)
    scene.collection.objects.link(light_ob)
    light_ob.location = -3.0716, 8.1817, 6.4709
    light_ob.rotation_euler = 37.3, 3.16, 107
    light_ob.data.energy = 200
    light_ob.data.color= (1,1,1)


    light_data2 = bpy.data.lights.new("MyLight2", 'POINT')
    light_ob2 = bpy.data.objects.new(name="MyLight2", object_data=light_data2)
    scene.collection.objects.link(light_ob2)
    light_ob2.location = 1.6804, -2.5547, 3.2763
    light_ob2.rotation_euler = 37.3, 3.16, 107
    light_ob2.data.energy = 200
    light_ob2.data.color= (1,1,1)


    light_data3 = bpy.data.lights.new("MyLight3", 'POINT')
    light_ob3 = bpy.data.objects.new(name="MyLight3", object_data=light_data3)
    scene.collection.objects.link(light_ob3)
    light_ob3.location = 6.9779, 5.1226, 8.701
    light_ob3.rotation_euler = 37.3, 3.16, 107
    light_ob3.data.energy = 200
    light_ob3.data.color= (1,1,1)

    ## set invisible plane (shadow catcher)
    #invisibleGround(shadowBrightness=0.9)


    bpy.context.view_layer.update()

    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=blend_filename)

    render = scene.render
    render.use_file_extension = True
    render.filepath = png_filename
    render.resolution_x = 640
    render.resolution_y = 480
    bpy.ops.render.render(write_still=True)



def render_piece(mypiece, suffix, save_blend=False):
    filepath = os.getcwd()
    blend_filename = f"{filepath}/piece{suffix}.blend"
    png_filename = f"{filepath}/piece{suffix}.png"
    
    # Clear existing objects.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    scene = bpy.context.scene
    
    #set transparent background
    scene.render.film_transparent = True


    size = 0.2
    coord = 2*size
    i = 0
    cubecolor=204/255,170/255,155/255,1
    beamcolor=89/255,71/255,53/255,1
    cubecolor, beamcolor = get_piece_colors(mypiece)
    mat = bpy.data.materials.new("cubecolor")
    mat.diffuse_color = cubecolor

    Bl = np.zeros((5,5,5), dtype = int)
    for block in mypiece.blocks: 
        c = block.pos
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.selected_objects[0]
        cube.name = f"cube{i}"
        cube.location=(coord*c.x, coord*c.y, coord*c.z)
        bpy.ops.transform.resize(value = (size, size, size))
        cube.color = cubecolor
        cube.active_material = mat
        Bl[c.x, c.y, c.z] = 1
        i += 1
    
    i = 0
    sizeb=0.2
    coordb = 2*sizeb
    mat2 = bpy.data.materials.new("beamcolor")
    mat2.diffuse_color = beamcolor
    Be = np.zeros((5,5,5), dtype = int)
    for beam in mypiece.beams: 
        for block in beam:
            c = block.pos
            bpy.ops.mesh.primitive_cube_add()
            cube2 = bpy.context.selected_objects[0]
            cube2.name = f"beam{i}"
            cube2.location = (coordb*c.x, coordb*c.y, coordb*c.z)
            bpy.ops.transform.resize(value = (sizeb, sizeb, sizeb))
            cube2.color = beamcolor
            cube2.active_material = mat2
            Be[c.x, c.y, c.z] = 1
            i += 1

    V = Bl & Be

    assert(np.amax(V) == 0)

    # Camera
    cam_data = bpy.data.cameras.new("MyCam")
    cam_ob = bpy.data.objects.new(name="MyCam", object_data=cam_data)
    scene.collection.objects.link(cam_ob)  # instance the camera object in the scene
    scene.camera = cam_ob       # set the active camera
    
    pi = math.pi;
    cam_ob.rotation_mode = 'XYZ'
    ##pos cam 1
    #cam_ob.location = 7.3589, -6.9258, 4.9583
    #cam_ob.rotation_euler = 63.6*pi/180, 0*pi/180, 46.7*pi/180
    ##pos cam 2
    #cam_ob.location = 4.6027, 10.459, 6.329
    #cam_ob.rotation_euler = 63.6*pi/180, -0.394*pi/180, -201*pi/180
    ##pos cam 3
    cam_ob.location = -3.6678, -5.5478, 4.0441
    cam_ob.rotation_euler = 64.5*pi/180, -2.9*pi/180, -397*pi/180
    
    # Light
    light_data = bpy.data.lights.new("MyLight", 'POINT')
    light_ob = bpy.data.objects.new(name="MyLight", object_data=light_data)
    scene.collection.objects.link(light_ob)
    light_ob.location = -3.0447, -2.5547, 2.6529
    light_ob.rotation_euler = 37.3, 3.16, 107
    light_ob.data.energy = 200
    light_ob.data.color= (1,1,1)


    light_data2 = bpy.data.lights.new("MyLight2", 'POINT')
    light_ob2 = bpy.data.objects.new(name="MyLight2", object_data=light_data2)
    scene.collection.objects.link(light_ob2)
    light_ob2.location = 2.0506, -3.9892, 1.4709
    light_ob2.rotation_euler = 37.3, 3.16, 107
    light_ob2.data.energy = 200
    light_ob2.data.color= (1,1,1)

    ## set invisible plane (shadow catcher)
    #invisibleGround(shadowBrightness=0.9)

    
    bpy.context.view_layer.update()
    
    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=blend_filename)
    
    render = scene.render
    render.use_file_extension = True
    render.filepath = png_filename
    render.resolution_x = 640
    render.resolution_y = 480
    bpy.ops.render.render(write_still=True)


def invisibleGround(location = (0,0,0), groundSize = 100, shadowBrightness = 0.7):
	# initialize a ground for shadow
	bpy.context.scene.cycles.film_transparent = True
	bpy.ops.mesh.primitive_plane_add(location = location, size = groundSize)
	try:
		bpy.context.object.is_shadow_catcher = True # for blender 3.X
	except:
		bpy.context.object.cycles.is_shadow_catcher = True # for blender 2.X

	# # set material
	ground = bpy.context.object
	mat = bpy.data.materials.new('MeshMaterial')
	ground.data.materials.append(mat)
	mat.use_nodes = True
	tree = mat.node_tree
	tree.nodes["Principled BSDF"].inputs['Transmission'].default_value = shadowBrightness



def main():
    states = solve.umount_puzzle()
    for (state, i) in zip(states, range(len(states))):
        render_state(state, i)

    pieces = piece.get_result()
    for p in pieces:
        i = p.name[1]
        render_piece(p, i)

main()
