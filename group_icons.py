import os
import cairocffi
from xdg.IconTheme import getIconPath
from libqtile import hook, bar
from libqtile.images import Img
from libqtile.widget import base

from .icon_utils import _get_class_icon, _get_theme_icon, _get_fallback_icon, _get_custom_icon, get_window_icon
from .mouse_callbacks import get_clicked, button_press, select_window


class GroupTaskList(base._Widget, base.PaddingMixin, base.MarginMixin):
    defaults = [
        ("font", "sans", "Font of the text"),
        ("fontsize", None, "Font pixel size. Calculated if None."),
        ("fontcolor", "ffffff", "Text color"),
        ("icon_size", 16, "Size of the window icons"),
        ("icon_spacing_left", 0, "Spacing to the left of the icons"),
        ("icon_spacing_right", 8, "Spacing to the right of the icons"),
        ("icon_alignment", "center", "Alignment of the icons (left/center/right)"),  # Nova opção
        ("padding_left", 0, "Padding on the left side"),
        ("padding_right", 0, "Padding on the right side"),
        ("margin_x", -20, "Margin on the X axis"),
        ("theme_mode", "preferred", "Icon theme mode (preferred or fallback)"),
        ("theme_path", None, "Path to the icon theme"),
        ("background_inactive", "334455", "Background color for inactive groups"),
        ("background_active", "005577", "Background color for active group"),
        ("background_empty", "333344", "Background color for empty groups"),
        ("fallback_icon", "/home/cadr/.config/qtile/unk.png", "Path to the fallback icon"),
        ("max_width", 135, "Maximum width of the widget"),
        ("min_width", 135, "Minimum width of the widget"),
        ("label_visibility", "None", "Visibility of the label (Always/Empty/None)"),
        ("label_position", "Center", "Position of the label (Left/Center)"),
        ("line_thickness_active", 1, "Thickness of the line under the active window"),
        ("line_thickness_inactive", 1, "Thickness of the line under the active window"),
        ("line_thickness_floating", 1, "Thickness of the line under the floating window"),
        ("line_thickness_minimized", 1, "Thickness of the line under the minimized window"),
        ("line_color_active", "00FF00", "Color of the line under the active window"),
        ("line_color_inactive", "000000", "Color of the line under the active window"),
        ("line_color_floating", "FF0000", "Color of the line under the floating window"),
        ("line_color_minimized", "FFFF00", "Color of the line under the minimized window"),
        ("line_offset", 5, "Offset of the line from the bottom of the icon"),
    ]

    def __init__(self, group_name=None, **config):
        base._Widget.__init__(self, length=bar.CALCULATED, **config)
        self.add_defaults(GroupTaskList.defaults)
        self.add_defaults(base.PaddingMixin.defaults)
        self.add_defaults(base.MarginMixin.defaults)
        self.icon_size = self.icon_size
        self.icon_spacing_left = self.icon_spacing_left
        self.icon_spacing_right = self.icon_spacing_right
        self.icon_alignment = self.icon_alignment  # Alinhamento dos ícones
        self._icons_cache = {}
        self.group_name = group_name
        self.clicked_window = None

    def _configure(self, qtile, bar):
        base._Widget._configure(self, qtile, bar)

        if self.fontsize is None:
            calc = self.bar.height - self.margin_y * 2 - self.borderwidth * 2 - self.padding_y * 2
            self.fontsize = max(calc, 1)

        self.drawer = self.bar.window.create_drawer(self.bar.width, self.bar.height)
        self.layout = self.drawer.textlayout(
            "", self.fontcolor, self.font, self.fontsize, None, markup=False
        )
        self.setup_hooks()

    def calculate_length(self):
        if self.group_name is None or self.group_name not in self.qtile.groups_map:
            return 0

        group = self.qtile.groups_map[self.group_name]
        icon_count = len(group.windows)
        text_layout = self.drawer.textlayout(self.group_name, self.fontcolor, self.font, self.fontsize, None)
        total_width = text_layout.width + icon_count * (self.icon_size + self.icon_spacing_left + self.icon_spacing_right) + self.padding_left + self.padding_right

        if total_width > self.max_width:
            total_width = self.max_width
        elif total_width < self.min_width:
            total_width = self.min_width

        return total_width

    def get_window_icon(self, window):
        return get_window_icon(window, self.theme_mode, self.theme_path, self.fallback_icon, self.icon_size, self._icons_cache)

    def draw_icon(self, surface, offset):
        if not surface:
            return

        x = offset + self.padding_x
        y = (self.bar.height - self.icon_size) // 2

        self.drawer.ctx.save()
        self.drawer.ctx.translate(x, y)
        self.drawer.ctx.set_source(surface)
        self.drawer.ctx.paint()
        self.drawer.ctx.restore()

    def draw_line(self, offset, window):
        x_start = offset + (self.icon_size // 2) - (self.line_thickness_active // 2)
        y = (self.bar.height + self.icon_size) // 2 + self.line_offset

        if window.minimized:
            color = self.line_color_minimized
            thickness = self.line_thickness_minimized
        elif window.floating:
            color = self.line_color_floating
            thickness = self.line_thickness_floating
        elif window == self.qtile.current_window:
            color = self.line_color_active
            thickness = self.line_thickness_active
        else:
            color = self.line_color_inactive
            thickness = self.line_thickness_inactive
          #  return

        self.drawer.set_source_rgb(color)
        self.drawer.ctx.set_line_width(thickness)
        self.drawer.ctx.move_to(x_start, y)
        self.drawer.ctx.line_to(x_start + self.icon_size, y)
        self.drawer.ctx.stroke()

    def draw(self):
        if self.group_name is None or self.group_name not in self.qtile.groups_map:
            return

        group = self.qtile.groups_map[self.group_name]

        if not group.windows and group.screen and group == self.qtile.current_group:
            background = self.background_active
        elif group.windows:
            if group.screen:
                background = self.background_active
            else:
                background = self.background_inactive
        else:
            background = self.background_empty

        self.drawer.clear(background)
        offset = self.padding_left

        group_text = self.group_name

        if self.label_visibility != "None" and (self.label_visibility == "Always" or (self.label_visibility == "Empty" and not group.windows)):
            text_layout = self.drawer.textlayout(group_text, self.fontcolor, self.font, self.fontsize, None)

            if self.label_visibility == "Empty" and self.label_position == "Center":
                offset = (self.calculate_length() - text_layout.width) // 2
            else:
                offset = self.padding_left

            text_layout.draw(offset, (self.bar.height - self.fontsize) // 2)
            offset += text_layout.width + self.margin_x

        # Calcula o offset inicial baseado no alinhamento dos ícones
        icon_total_width = len(group.windows) * (self.icon_size + self.icon_spacing_left + self.icon_spacing_right) - self.icon_spacing_right

        if self.icon_alignment == "center":
            offset += (self.calculate_length() - icon_total_width) // 2 - (self.icon_size // 2)
        elif self.icon_alignment == "right":
            offset += self.calculate_length() - icon_total_width - self.padding_right - (self.icon_size // 2)

        self._box_positions = []  # Modificado para armazenar as posições iniciais e finais

        for window in group.windows:
            icon = self.get_window_icon(window)
            if icon:
                start_position = offset
                self.draw_icon(icon, start_position)
                self.draw_line(start_position, window)  # Desenhar a linha sob o ícone
                end_position = start_position + self.icon_size
                self._box_positions.append((start_position, end_position))
                offset += self.icon_size + self.icon_spacing_right + self.icon_spacing_left

        total_width = offset + self.padding_right

        if total_width > self.max_width:
            total_width = self.max_width
        elif total_width < self.min_width:
            total_width = self.min_width

        self.drawer.draw(offsetx=self.offsetx, offsety=self.offsety, width=total_width)


    def button_press(self, x, y, button):
        button_press(self, x, y, button)


    def _hook_response(self, *args, **kwargs):
        self._icons_cache.clear()  # Clear the cache to force icon updates
        self.draw()
        self.bar.draw()

    def setup_hooks(self):
        hook.subscribe.client_managed(self._hook_response)
        hook.subscribe.client_urgent_hint_changed(self._hook_response)
        hook.subscribe.client_killed(self._hook_response)
        hook.subscribe.setgroup(self._hook_response)
        hook.subscribe.group_window_add(self._hook_response)
        hook.subscribe.current_screen_change(self._hook_response)
        hook.subscribe.changegroup(self._hook_response)
        hook.subscribe.client_focus(self._hook_response)


    def update_tasklist(self):
        self._icons_cache.clear()
        self.draw()
        self.bar.draw()
