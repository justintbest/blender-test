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


class OBJECT_OT_move_to_active_object_collection(bpy.types.Operator):
    bl_idname = "object.move_to_active_object_collection"
    bl_label = "Move to Active Object's Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active = context.active_object

        if not active:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}

        target_collections = list(active.users_collection)

        if not target_collections:
            self.report({'WARNING'}, "Active object is not in any collection")
            return {'CANCELLED'}

        for obj in context.selected_objects:
            if obj == active:
                continue
            for coll in list(obj.users_collection):
                coll.objects.unlink(obj)
            for coll in target_collections:
                coll.objects.link(obj)

        return {'FINISHED'}
