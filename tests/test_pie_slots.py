import unittest

from m3_grouppro_bridge.pie_slots import (
    PIE_SOUTHEAST,
    PIE_SOUTHWEST,
    PieSlotRouter,
    can_route_empty_pair,
)


class RecordingLayout:
    def __init__(self):
        self.events = []

    def operator(self, idname, **kwargs):
        self.events.append(("operator", idname, kwargs))
        return object()

    def separator(self):
        self.events.append(("separator",))

    def split(self):
        self.events.append(("split",))
        return object()


class PieSlotRouterTests(unittest.TestCase):
    def test_replaces_only_real_southwest_and_southeast_separators(self):
        layout = RecordingLayout()
        router = PieSlotRouter(
            layout,
            {
                PIE_SOUTHWEST: {
                    "operator": "object.gpro_makeunique",
                    "icon": "UNLINKED",
                    "text": "Make Unique  Ⓖ",
                },
                PIE_SOUTHEAST: {
                    "operator": "object.edit_grouppro",
                    "icon": "EMPTY_ARROWS",
                    "text": "Edit Group  Ⓖ",
                },
            },
        )

        for _ in range(6):
            router.separator()
        router.separator()
        router.separator()

        self.assertEqual(
            layout.events[-2:],
            [
                (
                    "operator",
                    "object.gpro_makeunique",
                    {"icon": "UNLINKED", "text": "Make Unique  Ⓖ"},
                ),
                (
                    "operator",
                    "object.edit_grouppro",
                    {"icon": "EMPTY_ARROWS", "text": "Edit Group  Ⓖ"},
                ),
            ],
        )

    def test_does_not_replace_an_occupied_slot(self):
        layout = RecordingLayout()
        router = PieSlotRouter(
            layout,
            {
                PIE_SOUTHWEST: {
                    "operator": "object.gpro_makeunique",
                    "icon": "UNLINKED",
                },
            },
        )

        for _ in range(6):
            router.separator()
        result = router.split()

        self.assertIsNotNone(result)
        self.assertEqual(layout.events[-1], ("split",))

    def test_routes_only_when_both_native_diagonal_slots_are_free(self):
        self.assertTrue(
            can_route_empty_pair(
                linked=False,
                is_local_asset=False,
                is_m3_group=False,
            )
        )
        self.assertFalse(
            can_route_empty_pair(
                linked=True,
                is_local_asset=False,
                is_m3_group=False,
            )
        )
        self.assertFalse(
            can_route_empty_pair(
                linked=False,
                is_local_asset=True,
                is_m3_group=False,
            )
        )
        self.assertFalse(
            can_route_empty_pair(
                linked=False,
                is_local_asset=False,
                is_m3_group=True,
            )
        )


if __name__ == "__main__":
    unittest.main()
