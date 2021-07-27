#
#  Render Setup
#  Load and save render settings.
#  Copyright Patrick Huang 2021
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

bl_info = {
    "name": "Render Setup",
    "description": "Load and save render settings.",
    "category": "Render",
    "author": "Patrick Huang <huangpatrick16777216@gmail.com>",
    "version": (0, 1, 1),
    "blender": (2, 80, 0),
    "location": "3D View > Sidebar > Render Setup",
    "doc_url": "https://github.com/phuang1024/blender_addons",
    "bug_url": "https://github.com/phuang1024/blender_addons/issues",
    "warning": "Untested",
}

import os
import time
import json
import bpy
from bpy.props import BoolProperty, EnumProperty, IntProperty, PointerProperty, StringProperty

PARENT = os.path.dirname(os.path.realpath(__file__))
DATA = os.path.join(PARENT, "rsetup.json")
MUTEX = os.path.join(PARENT, "rsetup.mutex")

DATA_PATHS = {
    "render": [
        "render.engine",
        "render.use_simplify",
        "render.simplify_subdivision",
        "render.simplify_subdivision_render",
        "render.use_motion_blur",
        "render.motion_blur_shutter",
        "render.film_transparent",
        "render.threads_mode",
        "render.threads",
        "render.tile_x",
        "render.tile_y",
        "render.use_high_quality_normals",
        "view_settings.exposure",
    ],
    "cycles": [
        "cycles.device",
        "cycles.samples",
        "cycles.preview_samples",
        "cycles.use_adaptive_sampling",
        "cycles.adaptive_threshold",
        "cycles.adaptive_min_samples",
        "cycles.use_denoising",
        "cycles.denoiser",
        "cycles.use_preview_denoising",
        "cycles.preview_denoiser",
        "cycles.max_bounces",
        "cycles.diffuse_bounces",
        "cycles.glossy_bounces",
        "cycles.transparent_max_bounces",
        "cycles.transmission_bounces",
        "cycles.volume_bounces",
        "cycles.motion_blur_position",
        "cycles.tile_order",
    ],
    "eevee": [
        "eevee.taa_render_samples",
        "eevee.taa_samples",
        "eevee.use_taa_reprojection",
        "eevee.use_gtao",
        "eevee.gtao_distance",
        "eevee.use_bloom",
        "eevee.bloom_threshold",
        "eevee.use_ssr",
        "eevee.use_ssr_refraction",
        "eevee.use_motion_blur",
        "eevee.motion_blur_position",
        "eevee.motion_blur_shutter",
        "eevee.shadow_cube_size",
        "eevee.shadow_cascade_size",
        "eevee.use_shadow_high_bitdepth",
        "eevee.use_soft_shadows",
    ],
    "output": [
        "render.resolution_x",
        "render.resolution_y",
        "render.resolution_percentage",
        "render.fps",
        "render.filepath",
        "render.image_settings.file_format",
        "render.ffmpeg.format",
        "render.ffmpeg.codec",
        "render.ffmpeg.constant_rate_factor",
        "render.ffmpeg.audio_codec",
    ]
}


def multigetattr(obj, path):
    """Can handle paths with multiple dots."""
    paths = path.split(".")
    for p in paths:
        obj = getattr(obj, p)
    return obj

def multisetattr(obj, path, value):
    paths = path.split(".")
    for p in paths[:-1]:
        obj = getattr(obj, p)
    setattr(obj, paths[-1], value)


def mutex_check():
    """
    Returns if another process is using the file
    Read docstring in ``mutex_on`` for info about how the mutex works
    """
    if not os.path.isfile(MUTEX):
        return False
    with open(MUTEX, "r") as file:
        data = file.read(100)
        try:
            t = float(data)
            if time.time()-t < 0.1:
                return True
        except ValueError:
            return False

def mutex_on():
    """
    The file will contain a stringed ``time.time()``
    The mutex expires after 0.1 seconds, so if the mutex is not "offed",
    another process can use the file after 0.1 secs.
    """
    with open(MUTEX, "w") as file:
        file.write(str(time.time()))

def mutex_off():
    with open(MUTEX, "w") as file:
        file.write("0")

def load():
    while mutex_check():
        time.sleep(0.01)
    mutex_on()
    with open(DATA, "r") as file:
        obj = json.load(file)
    mutex_off()
    return obj

def dump(obj):
    while mutex_check():
        time.sleep(0.01)
    mutex_on()
    with open(DATA, "w") as file:
        json.dump(obj, file, indent=4)
    mutex_off()


def get_setups(scene, context):
    data = load()
    setups = [(key, key, key) for key in data]
    return setups


class RSETUP_Props(bpy.types.PropertyGroup):
    setup: EnumProperty(
        name="Setup",
        description="Choose the render setup.",
        items=get_setups
    )


class RSETUP_OT_New(bpy.types.Operator):
    """Add a new render setup."""
    bl_idname = "rsetup.new"
    bl_label = "New Setup"
    bl_description = "Add a new render setup."

    def execute(self, context):
        bpy.ops.rsetup.new_confirm("INVOKE_DEFAULT")
        return {"FINISHED"}

class RSETUP_OT_NewConfirm(bpy.types.Operator):
    """Show pop-up menu asking for name."""
    bl_idname = "rsetup.new_confirm"
    bl_label = "Add new setup?"
    bl_description = "Show pop-up menu asking for name."

    name: StringProperty(
        name="Setup Name",
        description="The setup name.",
    )

    inc_render: BoolProperty(name="Render", default=True)
    inc_cycles: BoolProperty(name="Cycles", default=True)
    inc_eevee: BoolProperty(name="Eevee", default=True)
    inc_output: BoolProperty(name="Output", default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")
        layout.label(text="Include in setup:")
        layout.prop(self, "inc_render")
        layout.prop(self, "inc_cycles")
        layout.prop(self, "inc_eevee")
        layout.prop(self, "inc_output")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        data = load()
        name = self.name

        if len(name) == 0:
            self.report({"ERROR"}, "Name cannot be empty.")
        elif name in data:
            self.report({"ERROR"}, "Setup name already exists.")
        else:
            paths = []
            if self.inc_render:
                paths.extend(DATA_PATHS["render"])
            if self.inc_cycles:
                paths.extend(DATA_PATHS["cycles"])
            if self.inc_eevee:
                paths.extend(DATA_PATHS["eevee"])
            if self.inc_output:
                paths.extend(DATA_PATHS["output"])

            data[name] = {path: multigetattr(context.scene, path) for path in paths}
            dump(data)
            self.report({"INFO"}, "Setup \"{}\" successfully added.".format(name))

        return {"FINISHED"}


class RSETUP_OT_Rm(bpy.types.Operator):
    """Remove a setup."""
    bl_idname = "rsetup.rm"
    bl_label = "Remove Setup"
    bl_description = "Remove a setup."

    def execute(self, context):
        bpy.ops.rsetup.rm_confirm("INVOKE_DEFAULT")
        return {"FINISHED"}

class RSETUP_OT_RmConfirm(bpy.types.Operator):
    """Pop-up for setup name."""
    bl_idname = "rsetup.rm_confirm"
    bl_label = "Remove render setup?"
    bl_description = "Pop-up for setup name."

    name: EnumProperty(
        name="Setup Name",
        description="Name of setup to remove",
        items=get_setups
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="The setup will be permanently deleted.")
        layout.prop(self, "name")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        data = load()
        name = self.name

        if name in data:
            data.pop(name, None)
            dump(data)
            self.report({"INFO"}, "Setup \"{}\" successfully deleted.".format(name))
        else:
            self.report({"ERROR"}, "Name not found.")

        return {"FINISHED"}


class RSETUP_OT_Apply(bpy.types.Operator):
    """Apply selected render setup."""
    bl_idname = "rsetup.apply"
    bl_label = "Apply Setup"
    bl_description = "Apply selected render setup."

    def execute(self, context):
        bpy.ops.rsetup.apply_confirm("INVOKE_DEFAULT")
        return {"FINISHED"}

class RSETUP_OT_ApplyConfirm(bpy.types.Operator):
    """Popup asking for setup name."""
    bl_idname = "rsetup.apply_confirm"
    bl_label = "Apply setup?"
    bl_description = "Popup asking for setup name."

    name: EnumProperty(
        name="Setup Name",
        description="Name of setup to remove",
        items=get_setups
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="The current settings will be overwritten.")
        layout.prop(self, "name")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        data = load()
        name = self.name

        if name in data:
            for key in data[name]:
                multisetattr(context.scene, key, data[name][key])
            self.report({"INFO"}, "Setup \"{}\" successfully applied.".format(name))
        else:
            self.report({"ERROR"}, "Name not found.")

        return {"FINISHED"}


class RSETUP_OT_ExportJson(bpy.types.Operator):
    """Export setups as JSON."""
    bl_idname = "rsetup.exp_json"
    bl_label = "Export JSON"
    bl_description = "Export setups as JSON."

    filepath: StringProperty(
        name="File Path",
        description="Output .json file path.",
        subtype="FILE_PATH",
    )

    indent: IntProperty(
        name="Indent",
        description="File indentation",
        default=4, min=0, soft_max=10,
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        data = load()
        with open(self.filepath, "w") as file:
            json.dump(data, file, indent=self.indent)

        return {"FINISHED"}

class RSETUP_OT_ImportJson(bpy.types.Operator):
    """Import JSON setups."""
    bl_idname = "rsetup.imp_json"
    bl_label = "Import JSON"
    bl_description = "Import JSON setups."

    filepath: StringProperty(
        name="File Path",
        description="Input .json file path.",
        subtype="FILE_PATH"
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        current_data = load()
        with open(self.filepath, "r") as file:
            new_data = json.load(file)

        for key in new_data:
            if key not in current_data:
                current_data[key] = new_data[key]

        dump(current_data)
        return {"FINISHED"}


class RSETUP_PT_Main(bpy.types.Panel):
    bl_idname = "RSETUP_PT_Main"
    bl_label = "Render Setup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Render Setup"

    def draw(self, context):
        props = context.scene.rsetup
        layout = self.layout

        layout.prop(props, "setup", text="Setups")

        col = layout.column(align=True)
        col.operator("rsetup.new")
        col.operator("rsetup.rm")
        col.operator("rsetup.apply")

class RSETUP_PT_IO(bpy.types.Panel):
    bl_idname = "RSETUP_PT_IO"
    bl_label = "Import/Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Render Setup"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"

        col = layout.column(align=True)
        col.operator("rsetup.exp_json")
        col.operator("rsetup.imp_json")


classes = (
    RSETUP_Props,

    RSETUP_OT_New,
    RSETUP_OT_NewConfirm,
    RSETUP_OT_Rm,
    RSETUP_OT_RmConfirm,
    RSETUP_OT_Apply,
    RSETUP_OT_ApplyConfirm,

    RSETUP_OT_ExportJson,
    RSETUP_OT_ImportJson,

    RSETUP_PT_Main,
    RSETUP_PT_IO,
)

def register():
    if not os.path.isfile(DATA):
        dump({})

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rsetup = PointerProperty(type=RSETUP_Props)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.rsetup

if __name__ == "__main__":
    register()
