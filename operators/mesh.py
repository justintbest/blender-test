import bpy
import bmesh


def _unwrap_to_grid(obj, context):
    """
    Snapshot all UV layers, remove them all, create only the target layer
    (fresh), run Follow Active Quads in complete isolation, return the bmesh
    plus the snapshot so the caller can restore other layers after scaling.
    """
    me = obj.data

    if context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    target_name = me.uv_layers.active.name if me.uv_layers else "UVMap"
    target_idx  = me.uv_layers.active_index if me.uv_layers else 0

    # Save every layer in its original order
    snapshot = []
    for layer in me.uv_layers:
        is_target = (layer.name == target_name)
        snapshot.append({
            'name':      layer.name,
            'is_target': is_target,
            # Non-target layers: save their UV data so we can restore it later
            'data': None if is_target else [(d.uv.x, d.uv.y) for d in layer.data],
        })

    # Remove ALL layers so the unwrap operator runs with zero interference
    while me.uv_layers:
        me.uv_layers.remove(me.uv_layers[0])

    # Create only the fresh target layer
    me.uv_layers.new(name=target_name)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.follow_active_quads(mode='LENGTH_AVERAGE')

    # Flush operator output into mesh data before reading via bmesh
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')

    bm = bmesh.from_edit_mesh(me)
    uv_layer = bm.loops.layers.uv.get(target_name)
    return bm, uv_layer, snapshot, target_idx


def _restore_uv_layers(obj, snapshot, target_idx):
    """
    After the scale step is committed, rebuild the full UV layer stack in the
    original order.  The target layer (the only one that currently exists) gets
    its scaled data preserved; all other layers get their saved data back.
    """
    me = obj.data

    # snapshot is empty only when the object had no UV layers at all before —
    # in that case one fresh layer already exists and there's nothing to restore
    if not snapshot:
        return

    # layer.data is only populated in Object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # The target is the only layer alive; capture its scaled UV coordinates
    target_data = [(d.uv.x, d.uv.y) for d in me.uv_layers[0].data]
    me.uv_layers.remove(me.uv_layers[0])

    # Recreate every layer in its original position
    for entry in snapshot:
        new_layer = me.uv_layers.new(name=entry['name'])
        uv_data   = target_data if entry['is_target'] else entry['data']
        for i, (u, v) in enumerate(uv_data):
            new_layer.data[i].uv = (u, v)

    me.uv_layers.active_index = min(target_idx, len(me.uv_layers) - 1)


class OBJECT_OT_uv_active_quads(bpy.types.Operator):
    bl_idname = "object.uv_active_quads"
    bl_label = "UV Active Quads"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'WARNING'}, "No active mesh object selected.")
            return {'CANCELLED'}

        bm, uv_layer, snapshot, target_idx = _unwrap_to_grid(obj, context)

        if uv_layer is None:
            self.report({'WARNING'}, "No UVs found after unwrap.")
            return {'CANCELLED'}

        all_uvs = [loop[uv_layer].uv for face in bm.faces for loop in face.loops]
        min_u = min(uv.x for uv in all_uvs)
        max_u = max(uv.x for uv in all_uvs)
        min_v = min(uv.y for uv in all_uvs)
        max_v = max(uv.y for uv in all_uvs)
        range_u = max_u - min_u
        range_v = max_v - min_v

        if range_u == 0 or range_v == 0:
            self.report({'WARNING'}, "UV range is zero — cannot scale.")
            return {'CANCELLED'}

        # Uniform scale — preserves aspect ratio, centers in 0-1 space
        scale    = 1.0 / max(range_u, range_v)
        offset_u = (1.0 - range_u * scale) / 2.0
        offset_v = (1.0 - range_v * scale) / 2.0

        for face in bm.faces:
            for loop in face.loops:
                uv = loop[uv_layer].uv
                uv.x = (uv.x - min_u) * scale + offset_u
                uv.y = (uv.y - min_v) * scale + offset_v

        bmesh.update_edit_mesh(obj.data)
        _restore_uv_layers(obj, snapshot, target_idx)
        return {'FINISHED'}


class OBJECT_OT_uv_active_quads_full(bpy.types.Operator):
    bl_idname = "object.uv_active_quads_full"
    bl_label = "UV Active Quads Full"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'WARNING'}, "No active mesh object selected.")
            return {'CANCELLED'}

        bm, uv_layer, snapshot, target_idx = _unwrap_to_grid(obj, context)

        if uv_layer is None:
            self.report({'WARNING'}, "No UVs found after unwrap.")
            return {'CANCELLED'}

        all_uvs = [loop[uv_layer].uv for face in bm.faces for loop in face.loops]
        min_u = min(uv.x for uv in all_uvs)
        max_u = max(uv.x for uv in all_uvs)
        min_v = min(uv.y for uv in all_uvs)
        max_v = max(uv.y for uv in all_uvs)
        range_u = max_u - min_u
        range_v = max_v - min_v

        if range_u == 0 or range_v == 0:
            self.report({'WARNING'}, "UV range is zero — cannot scale.")
            return {'CANCELLED'}

        # Independent U/V scale — stretches to fill full 0-1 space
        scale_u = 1.0 / range_u
        scale_v = 1.0 / range_v

        for face in bm.faces:
            for loop in face.loops:
                uv = loop[uv_layer].uv
                uv.x = (uv.x - min_u) * scale_u
                uv.y = (uv.y - min_v) * scale_v

        bmesh.update_edit_mesh(obj.data)
        _restore_uv_layers(obj, snapshot, target_idx)
        return {'FINISHED'}


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
