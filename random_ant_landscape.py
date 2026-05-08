import bpy
import random
import mathutils.noise as noise
from mathutils import Vector


class LandscapeProperties(bpy.types.PropertyGroup):
    seed: bpy.props.IntProperty(name="Seed", default=-1, min=-1, max=9999,
        description="Set to -1 for random, or a fixed number to reproduce a result")
    subdivisions: bpy.props.IntProperty(name="Subdivisions", default=64, min=8, max=256,
        description="Mesh detail level")
    size_x: bpy.props.FloatProperty(name="Size X", default=4.0, min=0.1, max=20.0)
    size_y: bpy.props.FloatProperty(name="Size Y", default=4.0, min=0.1, max=20.0)
    height: bpy.props.FloatProperty(name="Height", default=2.0, min=0.0, max=10.0)
    noise_scale: bpy.props.FloatProperty(name="Noise Scale", default=0.8, min=0.01, max=5.0,
        description="Lower = broader hills, higher = more detail")
    octaves: bpy.props.IntProperty(name="Octaves", default=4, min=1, max=8,
        description="Layers of noise detail")


class LANDSCAPE_OT_Generate(bpy.types.Operator):
    bl_idname = "landscape.generate"
    bl_label = "Generate Landscape"

    def execute(self, context):
        props = context.scene.landscape_props
        seed = props.seed if props.seed >= 0 else random.randint(0, 9999)
        random.seed(seed)
        print(f"Generating landscape with seed: {seed}")

        subdivisions = props.subdivisions
        size_x = props.size_x
        size_y = props.size_y
        height_scale = props.height
        noise_scale = props.noise_scale
        octaves = props.octaves
        offset_x = random.uniform(0, 100)
        offset_y = random.uniform(0, 100)

        verts = []
        faces = []

        for i in range(subdivisions + 1):
            for j in range(subdivisions + 1):
                x = (i / subdivisions - 0.5) * size_x
                y = (j / subdivisions - 0.5) * size_y
                z = noise.fractal(
                    Vector((x * noise_scale + offset_x, y * noise_scale + offset_y, 0.0)),
                    1.0, 2.0, octaves
                ) * height_scale
                verts.append((x, y, z))

        for i in range(subdivisions):
            for j in range(subdivisions):
                a = i * (subdivisions + 1) + j
                b = a + 1
                c = a + (subdivisions + 1) + 1
                d = a + (subdivisions + 1)
                faces.append((a, b, c, d))

        mesh = bpy.data.meshes.new(f"Landscape_{seed}")
        mesh.from_pydata(verts, [], faces)
        mesh.update()

        obj = bpy.data.objects.new(f"ANT_Landscape_{seed}", mesh)
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        print(f"Created: {obj.name}")
        return {'FINISHED'}


class LANDSCAPE_PT_Panel(bpy.types.Panel):
    bl_label = "Random Landscape"
    bl_idname = "LANDSCAPE_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Landscape"

    def draw(self, context):
        layout = self.layout
        props = context.scene.landscape_props

        layout.prop(props, "seed")
        layout.prop(props, "subdivisions")
        layout.separator()
        layout.prop(props, "size_x")
        layout.prop(props, "size_y")
        layout.prop(props, "height")
        layout.separator()
        layout.prop(props, "noise_scale")
        layout.prop(props, "octaves")
        layout.separator()
        layout.operator("landscape.generate", text="Generate", icon="RNDCURVE")


classes = [LandscapeProperties, LANDSCAPE_OT_Generate, LANDSCAPE_PT_Panel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.landscape_props = bpy.props.PointerProperty(type=LandscapeProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.landscape_props

# Unregister first in case script is re-run
try:
    unregister()
except Exception:
    pass

register()
print("Random Landscape panel registered — open the N panel in the 3D viewport and click 'Landscape'")
