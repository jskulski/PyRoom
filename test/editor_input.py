import gtk


def type_keys(key_sequence, basic_editor):
    for key in key_sequence:
        self._type_key(key, basic_editor)

def type_key(key_char, basic_editor):
    type_event = gtk.gdk.Event(gtk.gdk.KEY_PRESS)
    type_event.keyval = gtk.keysyms.__dict__.get(key_char)
    type_event.time = 0
    basic_editor.textbox.emit('key_press_event', type_event)

def retrieve_current_buffer_text(basic_editor):
    buffer = basic_editor.textbox.get_buffer()
    buffer_text = buffer.get_text(*buffer.get_bounds())

    tb = basic_editor.textbox
    buf = tb.get_buffer()
    print '-----------'
    print buf.get_text(*buf.get_bounds())
    print '-----------'

    return buffer_text
