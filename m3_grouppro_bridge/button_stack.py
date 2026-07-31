BRIDGE_MARKER = "m3_group_pro_bridge"
GROUP_PRO_BADGE = "Ⓖ"


def with_group_pro_badge(label):
    return f"{label}  {GROUP_PRO_BADGE}"


def make_operator_button(
    operator,
    *,
    icon="NONE",
    properties=None,
    bridge=False,
    text=None,
):
    """Create one button entry in MACHIN3tools' stacked-pie format."""
    button = {
        "type": "OPERATOR",
        "operator": operator,
        "scale": 1.4,
        "depress": False,
        "style_kwargs": {
            "active": True,
            "enabled": True,
            "alert": False,
        },
        # Deliberately omit "text" so Blender uses the operator's bl_label.
        "common_kwargs": {
            "icon": icon,
        },
    }

    if properties:
        button["props"] = properties

    if bridge:
        button[BRIDGE_MARKER] = True

    if text is not None:
        button["common_kwargs"]["text"] = text

    return button


def is_exact_bridge_pair(stack, operators):
    return (
        len(stack) == len(operators)
        and all(button.get(BRIDGE_MARKER, False) for button in stack)
        and {button.get("operator") for button in stack} == set(operators)
    )


def order_buttons(stack, operator_order):
    by_operator = {button["operator"]: button for button in stack}
    return tuple(by_operator[operator] for operator in operator_order)
