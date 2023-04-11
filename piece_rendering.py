import bpy
import sys       # to get command line args
import argparse  # to parse options for us and print a nice help message
import math
import piece
import numpy as np

def render_piece(number):
    pieces = piece.get_pieces()

    mypiece = pieces[number]
    print("coucou")

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
    cubecolor=115/255,72/255,49/255,1
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
    beamcolor=51/255,32/255,20/255,1
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

    print(f"Max in V: {np.amax(V)}")
    # Camera
    cam_data = bpy.data.cameras.new("MyCam")
    cam_ob = bpy.data.objects.new(name="MyCam", object_data=cam_data)
    scene.collection.objects.link(cam_ob)  # instance the camera object in the scene
    scene.camera = cam_ob       # set the active camera
    
    pi = math.pi;
    cam_ob.rotation_mode = 'XYZ'
    cam_ob.location = 7.3589, -6.9258, 4.9583
    cam_ob.rotation_euler = 63.6*pi/180, 0*pi/180, 46.7*pi/180
    
    # Light
    light_data = bpy.data.lights.new("MyLight", 'POINT')
    light_ob = bpy.data.objects.new(name="MyLight", object_data=light_data)
    scene.collection.objects.link(light_ob)
    light_ob.location = 4.05, -1.86, 2.7
    light_ob.rotation_euler = 37.3, 3.16, 107
    light_ob.data.energy = 200
    light_ob.data.color= (1,1,1)
    
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
