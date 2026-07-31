import sys
from functools import wraps

import bpy
from bpy.app.handlers import persistent

from .button_stack import make_operator_button, with_group_pro_badge
from .decision import (
    ADD,
    CLOSE,
    CREATE,
    EDIT,
    MAKE_UNIQUE,
    REMOVE,
    decide_actions,
)
from .pie_slots import (
    PIE_SOUTHEAST,
    PIE_SOUTHWEST,
    PieSlotRouter,
    can_route_empty_pair,
)


M3_MENU_ID = "MACHIN3_MT_modes_pie"
M3_METHOD = "add_contextual_group_button"
M3_DRAW_EMPTY = "draw_empty"
PATCH_MARKER = "_m3_group_pro_bridge_patch"
ORIGINAL_MARKER = "_m3_group_pro_bridge_original"
DRAW_EMPTY_PATCH_MARKER = "_m3_group_pro_bridge_draw_empty_patch"
DRAW_EMPTY_ORIGINAL_MARKER = "_m3_group_pro_bridge_draw_empty_original"

OPERATOR_ICONS = {
    CREATE: "COLLECTION_NEW",
    MAKE_UNIQUE: "UNLINKED",
    ADD: "ADD",
    REMOVE: "REMOVE",
    CLOSE: "OUTLINER_COLLECTION",
}

_patched_class = None
_original_method = None
_original_draw_empty = None
_route_pair_to_slots = False
_retry_count = 0
_last_error = None


def _find_group_detector():
    for module_name, module in tuple(sys.modules.items()):
        if (
            module_name == "GroupPro.helpers_group"
            or module_name.endswith(".GroupPro.helpers_group")
        ):
            detector = getattr(module, "is_any_inst_coll", None)
            if detector:
                return detector
    return None


def _get_operator(idname):
    namespace, operator_name = idname.split(".", 1)
    operator_namespace = getattr(bpy.ops, namespace, None)
    if operator_namespace is None:
        return None
    return getattr(operator_namespace, operator_name, None)


def _operator_exists(idname):
    operator = _get_operator(idname)
    if operator is None:
        return False
    try:
        operator.get_rna_type()
    except (AttributeError, RuntimeError):
        return False
    return True


def _operator_poll(idname):
    operator = _get_operator(idname)
    if operator is None:
        return False
    try:
        return bool(operator.poll())
    except (AttributeError, RuntimeError):
        return False


def _operator_label(idname):
    operator = _get_operator(idname)
    if operator is None:
        return idname
    try:
        return operator.get_rna_type().name
    except (AttributeError, RuntimeError):
        return idname


def _button_text(idname):
    return with_group_pro_badge(_operator_label(idname))


def _context_actions(context):
    if getattr(context, "mode", None) != "OBJECT":
        return ()

    detector = _find_group_detector()
    if detector is None:
        return ()

    active = getattr(context, "active_object", None)
    try:
        active_is_group = bool(active and detector(active))
    except Exception:
        active_is_group = False

    scene = getattr(context, "scene", None)
    editing = bool(scene and getattr(scene, "storedGroupSettings", ()))
    has_selection = bool(getattr(context, "selected_objects", ()))
    can_edit_active = active_is_group and _operator_poll(EDIT)

    actions = decide_actions(
        editing=editing,
        has_selection=has_selection,
        active_is_group=active_is_group,
        can_edit_active=can_edit_active,
    )
    return tuple(action for action in actions if _operator_exists(action))


def _icon_for(action, active):
    if action == EDIT:
        return (
            "EMPTY_ARROWS"
            if active and getattr(active, "type", None) == "EMPTY"
            else "OUTLINER_DATA_MESH"
        )
    return OPERATOR_ICONS.get(action, "NONE")


def _properties_for(action, active):
    if action == CREATE and active:
        return {"name": active.name}
    return None


def _append_group_pro_buttons(stack, context):
    actions = _context_actions(context)
    if _route_pair_to_slots and actions == (EDIT, MAKE_UNIQUE):
        return

    active = getattr(context, "active_object", None)
    for action in actions:
        stack.append(
            make_operator_button(
                action,
                icon=_icon_for(action, active),
                properties=_properties_for(action, active),
                bridge=True,
                text=_button_text(action),
            )
        )


def _report_draw_error(error):
    global _last_error

    message = f"{type(error).__name__}: {error}"
    if message != _last_error:
        print(f"[M3 Group Pro Bridge] Menu injection skipped: {message}")
        _last_error = message


def _resolve_m3_menu_class():
    return getattr(bpy.types, M3_MENU_ID, None)


def _resolve_m3_pies_module(menu_class):
    return sys.modules.get(getattr(menu_class, "__module__", ""))


def _restore_class(menu_class):
    restored = False

    current = getattr(menu_class, M3_METHOD, None)
    if current and getattr(current, PATCH_MARKER, False):
        original = getattr(current, ORIGINAL_MARKER, None)
        if original:
            setattr(menu_class, M3_METHOD, original)
            restored = True

    current_draw_empty = getattr(menu_class, M3_DRAW_EMPTY, None)
    if current_draw_empty and getattr(
        current_draw_empty,
        DRAW_EMPTY_PATCH_MARKER,
        False,
    ):
        original = getattr(
            current_draw_empty,
            DRAW_EMPTY_ORIGINAL_MARKER,
            None,
        )
        if original:
            setattr(menu_class, M3_DRAW_EMPTY, original)
            restored = True

    return restored


def _can_route_pair_to_empty_slots(pies_module, context, active, linked):
    if _context_actions(context) != (EDIT, MAKE_UNIQUE):
        return False

    is_local_asset = bool(pies_module.is_local_assembly_asset(active))
    is_m3_group = bool(
        active
        and getattr(active, "M3", None)
        and active.M3.is_group_empty
    )
    return can_route_empty_pair(
        linked=bool(linked),
        is_local_asset=is_local_asset,
        is_m3_group=is_m3_group,
    )


def _empty_slot_replacements(active):
    return {
        PIE_SOUTHWEST: {
            "operator": MAKE_UNIQUE,
            "icon": _icon_for(MAKE_UNIQUE, active),
            "text": _button_text(MAKE_UNIQUE),
        },
        PIE_SOUTHEAST: {
            "operator": EDIT,
            "icon": _icon_for(EDIT, active),
            "text": _button_text(EDIT),
        },
    }


def install_patch():
    global _patched_class, _original_method, _original_draw_empty, _last_error

    menu_class = _resolve_m3_menu_class()
    if menu_class is None:
        return False

    pies_module = _resolve_m3_pies_module(menu_class)
    if pies_module is None:
        return False

    current = getattr(menu_class, M3_METHOD, None)
    if current is None:
        return False

    if getattr(current, PATCH_MARKER, False):
        _patched_class = menu_class
        _original_method = getattr(current, ORIGINAL_MARKER, None)
    else:
        if _patched_class is not None and _patched_class is not menu_class:
            _restore_class(_patched_class)

        original = current

        @wraps(original)
        def bridged(self, stack, is_group_selectable_up=False):
            original(self, stack, is_group_selectable_up)
            try:
                _append_group_pro_buttons(stack, bpy.context)
            except Exception as error:
                _report_draw_error(error)

        setattr(bridged, PATCH_MARKER, True)
        setattr(bridged, ORIGINAL_MARKER, original)
        setattr(menu_class, M3_METHOD, bridged)

        _patched_class = menu_class
        _original_method = original

    draw_empty = getattr(menu_class, M3_DRAW_EMPTY, None)
    if draw_empty is None:
        return False

    if getattr(draw_empty, DRAW_EMPTY_PATCH_MARKER, False):
        _original_draw_empty = getattr(
            draw_empty,
            DRAW_EMPTY_ORIGINAL_MARKER,
            None,
        )
    else:
        original_draw_empty = draw_empty

        @wraps(original_draw_empty)
        def bridged_draw_empty(self, context, active, linked, pie):
            global _route_pair_to_slots

            try:
                route_pair = _can_route_pair_to_empty_slots(
                    pies_module,
                    context,
                    active,
                    linked,
                )
            except Exception as error:
                _report_draw_error(error)
                route_pair = False

            if not route_pair:
                return original_draw_empty(
                    self,
                    context,
                    active,
                    linked,
                    pie,
                )

            previous_route = _route_pair_to_slots
            _route_pair_to_slots = True
            try:
                routed_pie = PieSlotRouter(
                    pie,
                    _empty_slot_replacements(active),
                )
                return original_draw_empty(
                    self,
                    context,
                    active,
                    linked,
                    routed_pie,
                )
            finally:
                _route_pair_to_slots = previous_route

        setattr(bridged_draw_empty, DRAW_EMPTY_PATCH_MARKER, True)
        setattr(
            bridged_draw_empty,
            DRAW_EMPTY_ORIGINAL_MARKER,
            original_draw_empty,
        )
        setattr(menu_class, M3_DRAW_EMPTY, bridged_draw_empty)
        _original_draw_empty = original_draw_empty

    _last_error = None
    print("[M3 Group Pro Bridge] MACHIN3tools Modes Pie integration installed.")
    return True


def remove_patch():
    global _patched_class, _original_method, _original_draw_empty

    restored = False
    if _patched_class is not None:
        restored = _restore_class(_patched_class)

    current_class = _resolve_m3_menu_class()
    if current_class is not None and current_class is not _patched_class:
        restored = _restore_class(current_class) or restored

    _patched_class = None
    _original_method = None
    _original_draw_empty = None

    if restored:
        print("[M3 Group Pro Bridge] MACHIN3tools Modes Pie integration removed.")
    return restored


def _delayed_install():
    global _retry_count

    if install_patch():
        _retry_count = 0
        return None

    _retry_count += 1
    return 1.0 if _retry_count < 20 else None


@persistent
def _load_post(_filepath):
    install_patch()


def register():
    global _retry_count

    if _load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_load_post)

    _retry_count = 0
    if not install_patch() and not bpy.app.timers.is_registered(_delayed_install):
        bpy.app.timers.register(_delayed_install, first_interval=0.2)


def unregister():
    if _load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_load_post)

    if bpy.app.timers.is_registered(_delayed_install):
        bpy.app.timers.unregister(_delayed_install)

    remove_patch()
