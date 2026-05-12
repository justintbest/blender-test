import bpy

class MESH_OT_set_crease_one(bpy.types.Operator):
    bl_idname = "mesh.set_crease_one"
    bl_label = "Set Crease to 1"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
            bpy.ops.mesh.select_mode(type='EDGE')
            bpy.ops.transform.edge_crease(value=1)
        else:
            self.report({'WARNING'}, "No active mesh in Edit Mode")
        return {'FINISHED'}


class MESH_OT_set_crease_zero(bpy.types.Operator):
    bl_idname = "mesh.set_crease_zero"
    bl_label = "Set Crease to 0"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
            bpy.ops.mesh.select_mode(type='EDGE')
            bpy.ops.transform.edge_crease(value=-1)
        else:
            self.report({'WARNING'}, "No active mesh in Edit Mode")
        return {'FINISHED'}
