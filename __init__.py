bl_info = {
    "name": "Best Controls",
    "author": "Justin Best",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Best Controls",
    "description": "Best Controls panel: transforms, mesh tools, cleanup, and collections",
    "category": "3D View",
}

from . operators import (
    OBJECT_OT_move_to_active_collection,
    OBJECT_OT_add_copy_transforms_constraint,
    OBJECT_OT_copy_transforms_no_constraint,
    OBJECT_OT_reset_transforms,
    MESH_OT_set_crease_one,
    MESH_OT_set_crease_zero,
    BEST_OT_remap_duplicates,
    OBJECT_OT_make_single_user_quick,
)
from .panels import (
    VIEW3D_PT_move_to_active_collection,
    VIEW3D_PT_scene_custom_props_filtered,
)

classes = (
    OBJECT_OT_move_to_active_collection,
    OBJECT_OT_add_copy_transforms_constraint,
    OBJECT_OT_copy_transforms_no_constraint,
    OBJECT_OT_reset_transforms,
    MESH_OT_set_crease_one,
    MESH_OT_set_crease_zero,
    BEST_OT_remap_duplicates,
    OBJECT_OT_make_single_user_quick,
    VIEW3D_PT_move_to_active_collection,
    VIEW3D_PT_scene_custom_props_filtered,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
