CREATE = "object.create_grouppro"
EDIT = "object.edit_grouppro"
MAKE_UNIQUE = "object.gpro_makeunique"
ADD = "object.add_to_grouppro"
REMOVE = "object.remove_from_grouppro"
CLOSE = "object.close_grouppro"


def decide_actions(*, editing, has_selection, active_is_group, can_edit_active):
    """Return native Group Pro operators for the current simple context state."""
    if editing:
        if active_is_group and can_edit_active:
            return (EDIT, CLOSE)

        if has_selection:
            return (ADD, REMOVE, CLOSE)

        return (CLOSE,)

    if active_is_group and can_edit_active:
        return (EDIT, MAKE_UNIQUE)

    if has_selection:
        return (CREATE,)

    return ()
