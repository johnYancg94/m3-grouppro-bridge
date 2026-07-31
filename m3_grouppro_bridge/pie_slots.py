PIE_SOUTHWEST = 6
PIE_SOUTHEAST = 7


def can_route_empty_pair(*, linked, is_local_asset, is_m3_group):
    return not linked and not is_local_asset and not is_m3_group


class PieSlotRouter:
    """Replace selected top-level pie separators with real pie operators."""

    def __init__(self, layout, replacements):
        self._layout = layout
        self._replacements = replacements
        self._slot = 0

    def _consume(self, method_name, *args, **kwargs):
        slot = self._slot
        self._slot += 1
        replacement = self._replacements.get(slot)

        if replacement and method_name == "separator":
            operator_kwargs = {
                "icon": replacement.get("icon", "NONE"),
            }
            if "text" in replacement:
                operator_kwargs["text"] = replacement["text"]
            return self._layout.operator(
                replacement["operator"],
                **operator_kwargs,
            )

        return getattr(self._layout, method_name)(*args, **kwargs)

    def operator(self, *args, **kwargs):
        return self._consume("operator", *args, **kwargs)

    def separator(self, *args, **kwargs):
        return self._consume("separator", *args, **kwargs)

    def split(self, *args, **kwargs):
        return self._consume("split", *args, **kwargs)

    def box(self, *args, **kwargs):
        return self._consume("box", *args, **kwargs)

    def prop(self, *args, **kwargs):
        return self._consume("prop", *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._layout, name)
