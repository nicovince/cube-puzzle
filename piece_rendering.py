#To be called with 
# 'blender --background --python piece_rendering.py'
# will render all pieces in separate files

import bpy
import sys       # to get command line args
import argparse  # to parse options for us and print a nice help message
import math
import piece
import numpy as np

def render_piece(number):
    pieces = piece.get_pieces5()

    mypiece = pieces[number]

    save_blend=f"/home/julie/perso/nico/cube-puzzle/piece{number}.blend"
    save_png=f"/home/julie/perso/nico/cube-puzzle/piece{number}.png"
    
    # Clear existing objects.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    scene = bpy.context.scene
    
    #set transparent background
    scene.render.film_transparent = True


    size = 0.2
    coord = 2*size
    i = 0
    cubecolor=204/255,170/255,155/255,1
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
    beamcolor=89/255,71/255,53/255,1
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
    
    bpy.context.view_layer.update()
    
    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=save_blend)
    
    if save_png:
        render = scene.render
        render.use_file_extension = True
        render.filepath = save_png
        bpy.ops.render.render(write_still=True)

def main():
    for i in range(0,8):
        render_piece(i)


main()
