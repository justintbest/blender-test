import bpy


class OBJECT_OT_add_single_vertex(bpy.types.Operator):
    bl_idname = "object.add_single_vertex"
    bl_label = "Single Vertex"
    bl_description = "Add a single vertex at the 3D cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mesh = bpy.data.meshes.new("Vertex")
        mesh.from_pydata([(0, 0, 0)], [], [])
        mesh.update()
        obj = bpy.data.objects.new("Vertex", mesh)
        obj.location = context.scene.cursor.location.copy()
        context.collection.objects.link(obj)
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        return {'FINISHED'}


class OBJECT_OT_add_single_plane(bpy.types.Operator):
    bl_idname = "object.add_single_plane"
    bl_label = "Single Plane"
    bl_description = "Add a plane at the 3D cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.primitive_plane_add(location=context.scene.cursor.location)
        return {'FINISHED'}


class OBJECT_OT_add_single_cube(bpy.types.Operator):
    bl_idname = "object.add_single_cube"
    bl_label = "Single Cube"
    bl_description = "Add a cube at the 3D cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add(location=context.scene.cursor.location)
        return {'FINISHED'}
