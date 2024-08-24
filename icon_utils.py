import os
import cairocffi
from xdg.IconTheme import getIconPath
from libqtile.images import Img

def _get_class_icon(window, icon_size):
    if not getattr(window, "icons", False):
        return None

    icons = sorted(
        iter(window.icons.items()),
        key=lambda x: abs(icon_size - int(x[0].split("x")[0])),
    )
    icon = icons[0]
    width, height = map(int, icon[0].split("x")[0])

    img = cairocffi.ImageSurface.create_for_data(
        icon[1], cairocffi.FORMAT_ARGB32, width, height
    )

    return img

def _get_theme_icon(window, theme_path):
    classes = window.get_wm_class()

    if not classes:
        return None

    icon = None

    for cl in classes:
        for app in set([cl, cl.lower()]):
            icon = getIconPath(app, theme=theme_path)
            if icon is not None:
                break
        else:
            continue
        break

    if not icon:
        return None

    img = Img.from_path(icon)

    return img.surface

def _get_fallback_icon(fallback_icon):
    if fallback_icon:
        return Img.from_path(fallback_icon).surface
    return None

def _get_custom_icon(window_class):
    icon_path = os.path.join("/home/cadr/.config/qtile/task_icons", window_class)
    if os.path.exists(icon_path):
        return icon_path
    return None

def get_window_icon(window, theme_mode, theme_path, fallback_icon, icon_size, icons_cache):
    if not getattr(window, "icons", False) and theme_mode is None:
        return None

    cache = icons_cache.get(window.wid)
    if cache:
        return cache

    surface = None
    img = None

    window_class = window.get_wm_class()[0] if window.get_wm_class() else None
    if window_class:
        custom_icon_path = _get_custom_icon(window_class)
        if custom_icon_path:
            img = Img.from_path(custom_icon_path).surface

    if img is None and window.qtile.core.name == "x11":
        img = _get_class_icon(window, icon_size)

    if theme_mode == "preferred" or (theme_mode == "fallback" and img is None):
        xdg_img = _get_theme_icon(window, theme_path)
        if xdg_img:
            img = xdg_img

    if img is None:
        img = _get_fallback_icon(fallback_icon)

    if img is not None:
        surface = cairocffi.SurfacePattern(img)
        height = img.get_height()
        width = img.get_width()
        scaler = cairocffi.Matrix()
        if height != icon_size:
            sp = height / icon_size
            height = icon_size
            width /= sp
            scaler.scale(sp, sp)
        surface.set_matrix(scaler)

    icons_cache[window.wid] = surface
    return surface
