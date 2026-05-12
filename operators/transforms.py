import bpy

class OBJECT_OT_add_copy_transforms_constraint(bpy.types.Operator):
    bl_idname = "object.add_copy_transforms_constraint"
    bl_label = "Add Copy Transforms Constraint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        active = context.view_layer.objects.active
        selected = context.selected_objects

        if not active:
            self.report({'WARNING'}, "No active object")
            return {'CANCELLED'}

        for obj in selected:
            if obj != active:
                constraint = obj.constraints.new(type='COPY_TRANSFORMS')
                constraint.target = active

        return {'FINISHED'}


class OBJECT_OT_copy_transforms_no_constraint(bpy.types.Operator):
    bl_idname = "object.copy_transforms_no_constraint"
    bl_label = "Copy Transforms (No Constraint)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        source = context.active_object
        targets = [obj for obj in context.selected_objects if obj != source]

        source_world_matrix = source.matrix_world.copy()

        for obj in targets:
            if obj.parent:
                obj.matrix_local = (
                    obj.parent.matrix_world.inverted() @ source_world_matrix
                )
            else:
                obj.matrix_world = source_world_matrix.copy()

        return {'FINISHED'}


class OBJECT_OT_reset_transforms(bpy.types.Operator):
    bl_idname = "object.reset_transforms"
    bl_label = "Reset Transforms"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object

        obj.location = (0, 0, 0)
        obj.scale = (1, 1, 1)

        if obj.rotation_mode == 'QUATERNION':
            obj.rotation_quaternion = (1, 0, 0, 0)
        else:
            obj.rotation_euler = (0, 0, 0)

        return {'FINISHED'}
