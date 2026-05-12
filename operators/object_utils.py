import bpy

class OBJECT_OT_flip_x(bpy.types.Operator):
    bl_idname = "object.flip_x"
    bl_label = "Flip X"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.selected_objects:
            obj.scale.x *= -1
        return {'FINISHED'}
