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
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "3D View > Sidebar > Render Setup",
    "doc_url": "https://github.com/phuang1024/blender_addons",
    "bug_url": "https://github.com/phuang1024/blender_addons/issues",
    "warning": "In development",
}

import os
import time
import json
import bpy
from bpy.props import EnumProperty, PointerProperty, StringProperty

PARENT = os.path.dirname(os.path.realpath(__file__))
DATA = os.path.join(PARENT, "rsetup.json")
MUTEX = os.path.join(PARENT, "rsetup.mutex")


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

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name")

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
            data[name] = ""
            dump(data)
            self.report({"INFO"}, "Setup \"{}\" successfully added.".format(name))

        return {"FINISHED"}


class RSETUP_PT_Main(bpy.types.Panel):
    bl_idname = "RSETUP_PT_Main"
    bl_label = "Render Setup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Render Setup"

    def draw(self, context):
        layout = self.layout
        props = context.scene.rsetup

        layout.prop(props, "setup")
        layout.operator("rsetup.new")


classes = (
    RSETUP_Props,
    RSETUP_PT_Main,
    RSETUP_OT_New,
    RSETUP_OT_NewConfirm,
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
