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

import bpy
from bpy.props import PointerProperty


class RSETUP_Props(bpy.types.PropertyGroup):
    pass


class RSETUP_PT_Main(bpy.types.Panel):
    bl_idname = "RSETUP_UT_Main"
    bl_label = "Render Setup"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Render Setup"

    def draw(self, context):
        layout = self.layout

        layout.label(text="hi")


classes = (
    RSETUP_Props,
    RSETUP_PT_Main,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rsetup = PointerProperty(type=RSETUP_Props)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.rsetup

if __name__ == "__main__":
    register()
