import unittest

from m3_grouppro_bridge.decision import (
    ADD,
    CLOSE,
    CREATE,
    EDIT,
    MAKE_UNIQUE,
    REMOVE,
    decide_actions,
)


class DecideActionsTests(unittest.TestCase):
    def test_outside_group_with_no_selection_adds_nothing(self):
        self.assertEqual(
            decide_actions(
                editing=False,
                has_selection=False,
                active_is_group=False,
                can_edit_active=False,
            ),
            (),
        )

    def test_outside_group_with_normal_selection_offers_create(self):
        self.assertEqual(
            decide_actions(
                editing=False,
                has_selection=True,
                active_is_group=False,
                can_edit_active=False,
            ),
            (CREATE,),
        )

    def test_outside_group_with_active_group_offers_edit_and_unique(self):
        self.assertEqual(
            decide_actions(
                editing=False,
                has_selection=True,
                active_is_group=True,
                can_edit_active=True,
            ),
            (EDIT, MAKE_UNIQUE),
        )

    def test_editing_with_no_selection_only_offers_close(self):
        self.assertEqual(
            decide_actions(
                editing=True,
                has_selection=False,
                active_is_group=False,
                can_edit_active=False,
            ),
            (CLOSE,),
        )

    def test_editing_with_selection_offers_native_add_remove_and_close(self):
        self.assertEqual(
            decide_actions(
                editing=True,
                has_selection=True,
                active_is_group=False,
                can_edit_active=False,
            ),
            (ADD, REMOVE, CLOSE),
        )

    def test_editing_with_editable_nested_group_prioritizes_edit_and_close(self):
        self.assertEqual(
            decide_actions(
                editing=True,
                has_selection=True,
                active_is_group=True,
                can_edit_active=True,
            ),
            (EDIT, CLOSE),
        )

    def test_group_that_native_operator_cannot_edit_falls_back_to_selection(self):
        self.assertEqual(
            decide_actions(
                editing=True,
                has_selection=True,
                active_is_group=True,
                can_edit_active=False,
            ),
            (ADD, REMOVE, CLOSE),
        )


if __name__ == "__main__":
    unittest.main()
