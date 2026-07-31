import os
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import addon_utils
import bpy


PROJECT_ROOT = Path(__file__).resolve().parents[1]
M3_ADDONS = Path(
    os.environ.get("M3_ADDONS_PATH")
    or bpy.utils.user_resource("SCRIPTS", path="addons")
)

sys.path.insert(0, str(M3_ADDONS))
sys.path.insert(0, str(PROJECT_ROOT))

from m3_grouppro_bridge import integration
from m3_grouppro_bridge.decision import (
    ADD,
    CLOSE,
    CREATE,
    EDIT,
    MAKE_UNIQUE,
    REMOVE,
)


def make_operator(class_name, idname):
    return type(
        class_name,
        (bpy.types.Operator,),
        {
            "bl_idname": idname,
            "bl_label": class_name,
            "execute": lambda self, context: {"FINISHED"},
        },
    )


operator_classes = [
    make_operator("OBJECT_OT_bridge_create", CREATE),
    make_operator("OBJECT_OT_bridge_edit", EDIT),
    make_operator("OBJECT_OT_bridge_unique", MAKE_UNIQUE),
    make_operator("OBJECT_OT_bridge_add", ADD),
    make_operator("OBJECT_OT_bridge_remove", REMOVE),
    make_operator("OBJECT_OT_bridge_close", CLOSE),
]


try:
    addon_utils.enable("MACHIN3tools", default_set=True, persistent=False)
    assert "MACHIN3tools" in bpy.context.preferences.addons
    menu_class = bpy.types.MACHIN3_MT_modes_pie
    original = menu_class.add_contextual_group_button
    original_draw_empty = menu_class.draw_empty
    original_close_slot_methods = {
        method_name: getattr(menu_class, method_name)
        for method_name in integration.M3_CLOSE_SLOT_METHODS
    }
    pies_module = sys.modules[menu_class.__module__]

    for operator_class in operator_classes:
        bpy.utils.register_class(operator_class)

    helper_module = ModuleType("test.GroupPro.helpers_group")
    helper_module.is_any_inst_coll = lambda obj: bool(
        obj and getattr(obj, "is_group", False)
    )
    sys.modules[helper_module.__name__] = helper_module

    integration.register()
    patched = menu_class.add_contextual_group_button
    assert getattr(patched, integration.PATCH_MARKER, False)
    assert getattr(
        menu_class.draw_empty,
        integration.DRAW_EMPTY_PATCH_MARKER,
        False,
    )
    for method_name in integration.M3_CLOSE_SLOT_METHODS:
        assert getattr(
            getattr(menu_class, method_name),
            integration.CLOSE_SLOT_PATCH_MARKER,
            False,
        )

    untouched_stack = []
    menu_class.add_contextual_group_button(
        SimpleNamespace(
            show_select_group_up=False,
            show_select_group=False,
            show_create_group=False,
        ),
        untouched_stack,
    )
    assert [button["operator"] for button in untouched_stack] == [CREATE]

    ordinary = SimpleNamespace(name="Cube", type="MESH", is_group=False)
    group = SimpleNamespace(
        name="Building",
        type="EMPTY",
        is_group=True,
        M3=SimpleNamespace(is_group_empty=False),
    )
    outside_scene = SimpleNamespace(storedGroupSettings=[])
    editing_scene = SimpleNamespace(storedGroupSettings=[object()])

    assert integration._context_actions(
        SimpleNamespace(
            mode="OBJECT",
            active_object=ordinary,
            selected_objects=[ordinary],
            scene=outside_scene,
        )
    ) == (CREATE,)
    assert integration._context_actions(
        SimpleNamespace(
            mode="OBJECT",
            active_object=group,
            selected_objects=[group],
            scene=outside_scene,
        )
    ) == (EDIT, MAKE_UNIQUE)

    group_context = SimpleNamespace(
            mode="OBJECT",
            active_object=group,
            selected_objects=[group],
            scene=outside_scene,
    )
    assert integration._can_route_pair_to_empty_slots(
        SimpleNamespace(is_local_assembly_asset=lambda active: None),
        group_context,
        group,
        linked=None,
    )
    replacements = integration._empty_slot_replacements(group)
    assert replacements[6]["text"].endswith("  Ⓖ")
    assert replacements[7]["text"].endswith("  Ⓖ")
    assert integration._button_text(CREATE).endswith("  Ⓖ")
    assert integration._button_text(ADD).endswith("  Ⓖ")
    assert integration._button_text(REMOVE).endswith("  Ⓖ")
    assert integration._button_text(CLOSE).endswith("  Ⓖ")
    close_replacements = integration._close_slot_replacements(ordinary)
    assert close_replacements[7]["operator"] == CLOSE
    assert close_replacements[7]["text"].endswith("  Ⓖ")

    class RecordingPie:
        def __init__(self):
            self.events = []

        def separator(self):
            self.events.append(("separator",))

        def operator(self, idname, **kwargs):
            self.events.append(("operator", idname, kwargs))
            return SimpleNamespace()

    routed_pie = RecordingPie()

    def draw_eight_empty_slots(_self, pie):
        for _ in range(8):
            pie.separator()

    integration._route_actions_during_draw(
        draw_eight_empty_slots,
        None,
        (routed_pie,),
        {},
        (CLOSE,),
        close_replacements,
    )
    assert routed_pie.events[-1][0:2] == ("operator", CLOSE)
    assert integration._routed_actions == frozenset()

    assert integration._context_actions(
        SimpleNamespace(
            mode="OBJECT",
            active_object=ordinary,
            selected_objects=[ordinary],
            scene=editing_scene,
        )
    ) == (ADD, REMOVE, CLOSE)

    previous_routed_actions = integration._routed_actions
    integration._routed_actions = frozenset((CLOSE,))
    try:
        stack = []
        integration._append_group_pro_buttons(
            stack,
            SimpleNamespace(
                mode="OBJECT",
                active_object=ordinary,
                selected_objects=[ordinary],
                scene=editing_scene,
            ),
        )
        assert [button["operator"] for button in stack] == [ADD, REMOVE]
    finally:
        integration._routed_actions = previous_routed_actions

    integration.unregister()
    assert menu_class.add_contextual_group_button is original
    assert menu_class.draw_empty is original_draw_empty
    for method_name, original_method in original_close_slot_methods.items():
        assert getattr(menu_class, method_name) is original_method
    print("M3_GROUP_PRO_BRIDGE_SMOKE_OK")
finally:
    integration.unregister()
    sys.modules.pop("test.GroupPro.helpers_group", None)
    for operator_class in reversed(operator_classes):
        if hasattr(bpy.types, operator_class.__name__):
            bpy.utils.unregister_class(operator_class)
    if "MACHIN3tools" in bpy.context.preferences.addons:
        addon_utils.disable("MACHIN3tools", default_set=True)
