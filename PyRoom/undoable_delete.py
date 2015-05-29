class UndoableDelete(object):
    """something that has ben deleted from our textbuffer"""
    def __init__(self, text_buffer, start_iter, end_iter):
        self.deleted_text = text_buffer.get_text(start_iter, end_iter)
        self.start = start_iter.get_offset()
        self.end = end_iter.get_offset()
        # need to find out if backspace or delete key has been used
        # so we don't mess up during redo
        insert_iter = text_buffer.get_iter_at_mark(text_buffer.get_insert())
        if insert_iter.get_offset() <= self.start:
            self.delete_key_used = True
        else:
            self.delete_key_used = False
        if self.end - self.start > 1 or self.deleted_text in ("\r", "\n", " "):
            self.mergeable = False
        else:
            self.mergeable = True
