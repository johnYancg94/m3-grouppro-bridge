import unittest

from m3_grouppro_bridge.button_stack import (
    is_exact_bridge_pair,
    make_operator_button,
    order_buttons,
    with_group_pro_badge,
)


class MakeOperatorButtonTests(unittest.TestCase):
    def test_matches_m3_stack_shape(self):
        button = make_operator_button("object.edit_grouppro", icon="EMPTY_ARROWS")

        self.assertEqual(button["type"], "OPERATOR")
        self.assertEqual(button["operator"], "object.edit_grouppro")
        self.assertEqual(button["scale"], 1.4)
        self.assertFalse(button["depress"])
        self.assertEqual(
            button["style_kwargs"],
            {"active": True, "enabled": True, "alert": False},
        )

    def test_omits_text_to_inherit_native_operator_label(self):
        button = make_operator_button("object.close_grouppro", icon="OUTLINER_COLLECTION")

        self.assertNotIn("text", button["common_kwargs"])
        self.assertEqual(button["common_kwargs"]["icon"], "OUTLINER_COLLECTION")

    def test_includes_operator_properties_only_when_given(self):
        without_properties = make_operator_button("object.create_grouppro")
        with_properties = make_operator_button(
            "object.create_grouppro",
            properties={"name": "Building"},
        )

        self.assertNotIn("props", without_properties)
        self.assertEqual(with_properties["props"], {"name": "Building"})

    def test_recognizes_only_the_exact_bridge_pair(self):
        edit = make_operator_button("object.edit_grouppro", bridge=True)
        unique = make_operator_button("object.gpro_makeunique", bridge=True)
        close = make_operator_button("object.close_grouppro", bridge=True)

        self.assertTrue(
            is_exact_bridge_pair(
                [edit, unique],
                ("object.edit_grouppro", "object.gpro_makeunique"),
            )
        )
        self.assertFalse(
            is_exact_bridge_pair(
                [edit, unique, close],
                ("object.edit_grouppro", "object.gpro_makeunique"),
            )
        )
        self.assertFalse(
            is_exact_bridge_pair(
                [
                    make_operator_button("object.edit_grouppro"),
                    make_operator_button("object.gpro_makeunique"),
                ],
                ("object.edit_grouppro", "object.gpro_makeunique"),
            )
        )

    def test_orders_unique_left_and_edit_right(self):
        edit = make_operator_button("object.edit_grouppro", bridge=True)
        unique = make_operator_button("object.gpro_makeunique", bridge=True)

        ordered = order_buttons(
            [edit, unique],
            ("object.gpro_makeunique", "object.edit_grouppro"),
        )

        self.assertEqual(
            [button["operator"] for button in ordered],
            ["object.gpro_makeunique", "object.edit_grouppro"],
        )

    def test_appends_circled_g_badge_to_native_label(self):
        self.assertEqual(
            with_group_pro_badge("Edit Group"),
            "Edit Group  Ⓖ",
        )

    def test_explicit_badged_text_is_forwarded_to_m3(self):
        button = make_operator_button(
            "object.edit_grouppro",
            text="Edit Group  Ⓖ",
            bridge=True,
        )

        self.assertEqual(
            button["common_kwargs"]["text"],
            "Edit Group  Ⓖ",
        )


if __name__ == "__main__":
    unittest.main()
