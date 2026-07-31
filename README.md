# M3 Group Pro Bridge

An independent Blender add-on by **JohnYan** that adds a small set of contextual
Group Pro actions to the MACHIN3tools Modes Pie opened with `Tab`.

It does not modify or redistribute MACHIN3tools or Group Pro. Both add-ons remain
separate dependencies and keep their original shortcuts and functionality.

> This project is not affiliated with or endorsed by the authors of
> MACHIN3tools or Group Pro.

## Features

- Adds only frequently used Group Pro actions to the M3 Modes Pie.
- Uses Group Pro's native operators instead of reimplementing group behavior.
- Keeps the original Group Pro Pie shortcut available for less frequent actions.
- Marks bridged actions with a trailing `Ⓖ` badge.
- Uses real Pie slots when available to prevent visual buttons from overlapping
  neighboring gesture hot zones.
- Restores the original M3 methods when the bridge is disabled.
- Safely hides its additions if M3 or Group Pro is unavailable.

## Requirements

The initial release has been tested with:

- Blender 5.2 LTS
- MACHIN3tools 1.13.11.DeusEx
- Group Pro installed as a Blender extension

Other versions may work, but have not yet been verified.

## Installation

1. Download this repository as a ZIP and extract it.
2. Copy the inner `m3_grouppro_bridge` folder to:

   ```text
   %APPDATA%\Blender Foundation\Blender\<version>\scripts\addons\
   ```

3. Open Blender preferences and go to **Add-ons**.
4. Search for **M3 Group Pro Bridge** and enable it.
5. Ensure MACHIN3tools and Group Pro are also installed and enabled.
6. In MACHIN3tools preferences, ensure the Modes Pie is enabled and assigned to
   `Tab`.

The final folder should look like:

```text
scripts/
└── addons/
    └── m3_grouppro_bridge/
        ├── __init__.py
        ├── button_stack.py
        ├── decision.py
        ├── integration.py
        └── pie_slots.py
```

## Usage

In the 3D Viewport, press `Tab` to open the MACHIN3tools Modes Pie. The bridge
adds Group Pro actions according to the current Object Mode context:

| Context | Added actions |
| --- | --- |
| Nothing selected | None |
| Ordinary objects selected | `Create Group Ⓖ` |
| A Group Pro instance is active | `Make Unique Ⓖ`, `Edit Group Ⓖ` |
| Editing a group with no selection | `Close Group Ⓖ` |
| Editing a group with selected objects | `Add to Group Ⓖ`, `Remove from Group Ⓖ`, `Close Group Ⓖ` |
| An editable nested group is active | `Edit Group Ⓖ`, `Close Group Ⓖ` |

For an unlinked Empty group instance, `Make Unique Ⓖ` and `Edit Group Ⓖ` use
separate southwest and southeast Pie slots. If those slots are already occupied
by M3, the bridge falls back without replacing the existing M3 actions.

## Development and verification

Run the Blender-independent tests with Blender's bundled Python:

```powershell
& "<Blender>\5.2\python\bin\python.exe" -m unittest discover -s tests -v
```

Run the integration smoke test:

```powershell
& "<Blender>\blender.exe" --background --factory-startup --python tests\blender_smoke.py
```

If MACHIN3tools is stored in a non-default add-ons directory, set
`M3_ADDONS_PATH` before running the smoke test.

## 中文说明

M3 Group Pro Bridge 是由 **JohnYan** 制作的独立桥接插件。它会把 Group Pro
中常用的创建组、编辑组、关闭组、添加/移除成员和独立化等操作，按当前选择状态
加入 MACHIN3tools 的 `Tab` 模式 Pie 菜单。

插件不会修改或包含 MACHIN3tools 与 Group Pro 的源码。安装时只需把
`m3_grouppro_bridge` 文件夹复制到 Blender 用户插件目录，然后在偏好设置中启用。
使用时在 3D 视图的 Object Mode 按 `Tab`；带有 `Ⓖ` 后缀的按钮即为 Group Pro
桥接功能。Group Pro 原生 Pie 菜单及其快捷键仍然保留。

## License

This project is released under the GNU General Public License v3.0. See
`LICENSE` for the full text.
