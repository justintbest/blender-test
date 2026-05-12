import bpy

class OBJECT_OT_move_to_active_collection(bpy.types.Operator):
    bl_idname = "object.move_to_active_collection"
    bl_label = "Move to Active Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active_coll = context.view_layer.active_layer_collection.collection

        for obj in context.selected_objects:
            for coll in obj.users_collection:
                coll.objects.unlink(obj)
            active_coll.objects.link(obj)

        return {'FINISHED'}
