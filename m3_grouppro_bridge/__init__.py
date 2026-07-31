bl_info = {
    "name": "M3 Group Pro Bridge",
    "author": "JohnYan",
    "version": (0, 4, 1),
    "blender": (4, 2, 0),
    "location": "3D View > MACHIN3tools Modes Pie (Tab)",
    "description": "Adds contextual Group Pro actions to the MACHIN3tools Modes Pie",
    "category": "3D View",
}


def register():
    from . import integration

    integration.register()


def unregister():
    from . import integration

    integration.unregister()
