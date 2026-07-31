# M3 Group Pro Bridge

A Blender add-on that adds a small set of contextual Group Pro actions to the
MACHIN3tools Modes Pie opened with `Tab`.

It does not modify or redistribute MACHIN3tools or Group Pro. Both add-ons remain
separate dependencies and keep their original shortcuts and functionality.

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

1. Download `m3-grouppro-bridge-v0.4.0.zip` from the
   [latest release](https://github.com/johnYancg94/m3-grouppro-bridge/releases/latest).
2. Open Blender preferences and go to **Add-ons**.
3. Open the add-on menu, choose **Install from Disk**, and select the downloaded
   ZIP file.
4. Search for **M3 Group Pro Bridge** and enable it.
5. Ensure MACHIN3tools and Group Pro are also installed and enabled.
6. In MACHIN3tools preferences, ensure the Modes Pie is enabled and assigned to
   `Tab`.

For manual installation, extract the ZIP and copy the
`m3_grouppro_bridge` folder to:

```text
%APPDATA%\Blender Foundation\Blender\<version>\scripts\addons\
```

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

## 中文说明

M3 Group Pro Bridge 会把 Group Pro 中常用的创建组、编辑组、关闭组、
添加/移除成员和独立化等操作，按当前选择状态加入 MACHIN3tools 的 `Tab`
模式 Pie 菜单。

插件不会修改或包含 MACHIN3tools 与 Group Pro 的源码。安装时只需把
Release 页面中的 ZIP 通过 Blender 的 **Install from Disk** 安装并启用。
使用时在 3D 视图的 Object Mode 按 `Tab`；带有 `Ⓖ` 后缀的按钮即为
Group Pro 桥接功能。Group Pro 原生 Pie 菜单及其快捷键仍然保留。
