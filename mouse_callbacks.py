from libqtile.log_utils import logger
from libqtile import qtile
import itertools

def get_clicked(widget, x, y):
    for (box_start, box_end), win in zip(widget._box_positions, widget.qtile.groups_map[widget.group_name].windows):
        if (box_start + widget.icon_size // 2) <= x <= (box_end + widget.icon_size // 2):
            return win
    return None

def button_press(widget, x, y, button):
    widget.clicked_window = get_clicked(widget, x, y)
    if button == 1:
        group = qtile.groups_map[widget.group_name]
        if qtile.current_group != group:
            qtile.current_screen.set_group(group)
        else: 
            if widget.clicked_window:
                select_window(widget)
                
    elif button == 4:  # Scroll up
        change_group(widget, "prev")
    elif button == 5:  # Scroll down
        change_group(widget, "next")

def select_window(widget):
    if widget.clicked_window:
        current_win = widget.bar.screen.group.current_window
        window = widget.clicked_window
        if window is not current_win:
            window.group.focus(window, False)
            if window.floating:
                window.bring_to_front()
        else:
            window.toggle_minimize()

def change_group(widget, direction):
    current_group = qtile.current_group
    filtered_groups = [g for g in qtile.groups if g.name in widget.scroll_groups]
    
    i = itertools.cycle(filtered_groups if direction == "next" else reversed(filtered_groups))
    
    while next(i) != current_group:
        pass
    
    for group in i:
        if group != current_group:
            qtile.current_screen.set_group(group, warp=False)
            break
