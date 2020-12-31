import gtk


def type_keys(key_sequence, editor):
    for key in key_sequence:
        type_key(key, editor)

def type_key(key_char, editor):
    type_event = gtk.gdk.Event(gtk.gdk.KEY_PRESS)

    if key_char == ' ':
        type_event.keyval = gtk.keysyms.space
    elif key_char == ',':
        type_event.keyval = gtk.keysyms.comma
    elif key_char == '?':
        type_event.keyval = gtk.keysyms.question
    else:
        type_event.keyval = gtk.keysyms.__dict__.get(key_char)

    type_event.time = 0
    editor.gui.textbox.emit('key_press_event', type_event)
    editor.get_current_buffer().set_text(
        # editor.gui.textbox.get_buffer_text()
        editor.gui.get_text_from_textbox()
    )
    editor.get_current_buffer().modified = True

def retrieve_current_buffer_text(editor):
    return editor.get_current_buffer().get_text_from_buffer()
