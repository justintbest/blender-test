import bpy

class BEST_OT_remap_duplicates(bpy.types.Operator):
    bl_idname = "best.remap_duplicates"
    bl_label = "Remap Duplicates"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        def get_original(datablocks, db):
            """Return the canonical (non-duplicate) version of db, or None."""
            if '.' not in db.name:
                return None
            parts = db.name.rsplit('.', 1)
            if len(parts) != 2 or not parts[1].isdigit():
                return None
            base_name = parts[0]
            if base_name not in datablocks:
                return None
            target = datablocks[base_name]
            if target.library or db.library:
                return None
            return target

        # --- Pass 1: Remap duplicate materials everywhere (slots + geo nodes) ---
        for db in list(bpy.data.materials):
            target = get_original(bpy.data.materials, db)
            if target is None:
                continue
            for obj in bpy.data.objects:
                if obj.library:
                    continue
                for i, slot in enumerate(obj.material_slots):
                    if slot.material == db:
                        if slot.link == 'DATA':
                            if obj.data and not obj.data.library:
                                obj.data.materials[i] = target
                        else:
                            slot.material = target
            for ng in bpy.data.node_groups:
                if ng.library:
                    continue
                for node in ng.nodes:
                    if node.type == 'SET_MATERIAL' and node.inputs:
                        mat_input = node.inputs.get('Material')
                        if mat_input and mat_input.default_value == db:
                            mat_input.default_value = target
            for obj in bpy.data.objects:
                if obj.library:
                    continue
                for mod in obj.modifiers:
                    if mod.type != 'NODES' or not mod.node_group:
                        continue
                    if mod.node_group.library:
                        continue
                    for socket in mod.node_group.interface.items_tree:
                        if socket.item_type != 'SOCKET':
                            continue
                        if socket.bl_socket_idname != 'NodeSocketMaterial':
                            continue
                        if socket.in_out != 'INPUT':
                            continue
                        identifier = socket.identifier
                        if mod.get(identifier) == db:
                            mod[identifier] = target

        # --- Pass 2: Delete duplicate materials now that all refs are gone ---
        for db in list(bpy.data.materials):
            target = get_original(bpy.data.materials, db)
            if target is None:
                continue
            db.use_fake_user = False
            try:
                bpy.data.materials.remove(db)
            except RuntimeError as e:
                print(f"Could not remove {db.name}: {e}")

        # --- Pass 3: Remap duplicate node groups everywhere ---
        for db in list(bpy.data.node_groups):
            if db.bl_idname == 'CompositorNodeTree':
                continue
            target = get_original(bpy.data.node_groups, db)
            if target is None:
                continue
            for ng in bpy.data.node_groups:
                if ng.library:
                    continue
                if ng.bl_idname == 'CompositorNodeTree':
                    continue
                for node in ng.nodes:
                    if node.type == 'GROUP' and node.node_tree == db:
                        node.node_tree = target
            for mat in bpy.data.materials:
                if mat.library:
                    continue
                if mat.use_nodes and mat.node_tree:
                    if mat.node_tree.library:
                        continue
                    for node in mat.node_tree.nodes:
                        if node.type == 'GROUP' and node.node_tree == db:
                            node.node_tree = target
            for world in bpy.data.worlds:
                if world.library:
                    continue
                if world.use_nodes and world.node_tree:
                    if world.node_tree.library:
                        continue
                    for node in world.node_tree.nodes:
                        if node.type == 'GROUP' and node.node_tree == db:
                            node.node_tree = target
            for obj in bpy.data.objects:
                if obj.library:
                    continue
                for mod in obj.modifiers:
                    if mod.type == 'NODES' and mod.node_group == db:
                        if not mod.node_group.library:
                            mod.node_group = target

        # --- Pass 4: Delete duplicate node groups now that all refs are gone ---
        for db in list(bpy.data.node_groups):
            if db.bl_idname == 'CompositorNodeTree':
                continue
            target = get_original(bpy.data.node_groups, db)
            if target is None:
                continue
            db.use_fake_user = False
            try:
                bpy.data.node_groups.remove(db)
            except RuntimeError as e:
                print(f"Could not remove {db.name}: {e}")

        return {'FINISHED'}


class OBJECT_OT_make_single_user_quick(bpy.types.Operator):
    bl_idname = "object.make_single_user_quick"
    bl_label = "Make Single User Quick"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.make_single_user(
            object=True,
            obdata=True,
            material=False,
            animation=False
        )
        return {'FINISHED'}
