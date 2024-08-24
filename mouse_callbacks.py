def get_clicked(widget, x, y):
    for (box_start, box_end), win in zip(widget._box_positions, widget.qtile.groups_map[widget.group_name].windows):
        if (box_start + widget.icon_size // 2) <= x <= (box_end + widget.icon_size // 2):
            return win
    return None
        
def button_press(widget, x, y, button):
    widget.clicked_window = get_clicked(widget, x, y)
    if button == 1 and widget.clicked_window:
        select_window(widget)
    base._Widget.button_press(widget, x, y, button)

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
