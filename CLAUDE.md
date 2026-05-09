# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Blender 4.2+ Python add-on that generates randomized terrain meshes using fractal Perlin noise. There is no build system, package manager, or test suite — the single script is run directly inside Blender's scripting workspace.

## Running the Script

This is not a standalone Python project. It must be executed inside Blender:

1. Open Blender → **Scripting** workspace
2. Open `random_ant_landscape.py`
3. Press **Alt+P** to run
4. Switch to the **3D Viewport**, press **N**, open the **Landscape** tab

The script self-registers on run (and safely unregisters first if already registered, so re-running is safe).

## Architecture

Everything lives in `random_ant_landscape.py` with three Blender types wired together:

- **`LandscapeProperties`** (`bpy.types.PropertyGroup`) — all user-facing parameters stored on `bpy.types.Scene.landscape_props`
- **`LANDSCAPE_OT_Generate`** (`bpy.types.Operator`) — reads from `context.scene.landscape_props`, generates a vertex grid using `mathutils.noise.fractal()` with random X/Y offsets seeded by `props.seed`, builds quad faces, and links the resulting mesh object into the active collection
- **`LANDSCAPE_PT_Panel`** (`bpy.types.Panel`) — draws the N-panel UI in `VIEW_3D`, exposes all properties, and triggers the operator

Seed handling: `seed == -1` picks a random seed at generation time via `random.randint`; any `>= 0` value is deterministic.

## Blender API Conventions

- Operator IDs follow `CATEGORY_OT_name`, panel IDs follow `CATEGORY_PT_name`
- `bl_idname` for the operator is `"landscape.generate"` (used in `layout.operator(...)`)
- Classes must be registered in dependency order; `unregister()` reverses that order
