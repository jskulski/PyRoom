import gtk

from undoable_insert import UndoableInsert
from undoable_delete import UndoableDelete


class UndoableBuffer(gtk.TextBuffer):
    """text buffer with added undo capabilities

    designed as a drop-in replacement for gtksourceview,
    at least as far as undo is concerned"""
    
    def __init__(self):
        """
        we'll need empty stacks for undo/redo and some state keeping
        """
        self.undo_stack = []
        self.redo_stack = []
        self.modified = False
        self.not_undoable_action = False
        self.undo_in_progress = False
        self.text_buffer = gtk.TextBuffer()
        self.text_buffer.connect('insert-text', self.on_insert_text)
        self.text_buffer.connect('delete-range', self.on_delete_range)
        self.text_buffer.connect('begin_user_action', self.on_begin_user_action)

    @property
    def can_undo(self):
        return bool(self.undo_stack)

    @property
    def can_redo(self):
        return bool(self.redo_stack)

    def on_insert_text(self, textbuffer, text_iter, text, length):
        def can_be_merged(prev, cur):
            """see if we can merge multiple inserts here

            will try to merge words or whitespace
            can't merge if prev and cur are not mergeable in the first place
            can't merge when user set the input bar somewhere else
            can't merge across word boundaries"""
            WHITESPACE = (' ', '\t')
            if not cur.mergeable or not prev.mergeable:
                return False
            if cur.offset != (prev.offset + prev.length):
                return False
            if cur.text in WHITESPACE and not prev.text in WHITESPACE:
                return False
            elif prev.text in WHITESPACE and not cur.text in WHITESPACE:
                return False
            return True

        if not self.undo_in_progress:
            self.redo_stack = []
        if self.not_undoable_action:
            return
        undo_action = UndoableInsert(text_iter, text, length)
        try:
            prev_insert = self.undo_stack.pop()
        except IndexError:
            self.undo_stack.append(undo_action)
            return
        if not isinstance(prev_insert, UndoableInsert):
            self.undo_stack.append(prev_insert)
            self.undo_stack.append(undo_action)
            return
        if can_be_merged(prev_insert, undo_action):
            prev_insert.length += undo_action.length
            prev_insert.text += undo_action.text
            self.undo_stack.append(prev_insert)
        else:
            self.undo_stack.append(prev_insert)
            self.undo_stack.append(undo_action)
        self.modified = True
        
    def on_delete_range(self, text_buffer, start_iter, end_iter):
        def can_be_merged(prev, cur):
            """see if we can merge multiple deletions here

            will try to merge words or whitespace
            can't merge if delete and backspace key were both used
            can't merge across word boundaries"""

            WHITESPACE = (' ', '\t')
            if prev.delete_key_used != cur.delete_key_used:
                return False
            if prev.start != cur.start and prev.start != cur.end:
                return False
            if cur.deleted_text not in WHITESPACE and \
               prev.deleted_text in WHITESPACE:
                return False
            elif cur.deleted_text in WHITESPACE and \
               prev.deleted_text not in WHITESPACE:
                return False
            return True

        if not self.undo_in_progress:
            self.redo_stack = []
        if self.not_undoable_action:
            return
        undo_action = UndoableDelete(text_buffer, start_iter, end_iter)
        try:
            prev_delete = self.undo_stack.pop()
        except IndexError:
            self.undo_stack.append(undo_action)
            return
        if not isinstance(prev_delete, UndoableDelete):
            self.undo_stack.append(prev_delete)
            self.undo_stack.append(undo_action)
            return
        if can_be_merged(prev_delete, undo_action):
            if prev_delete.start == undo_action.start: # delete key used
                prev_delete.deleted_text += undo_action.deleted_text
                prev_delete.end += (undo_action.end - undo_action.start)
            else: # Backspace used
                prev_delete.deleted_text = "%s%s" % (undo_action.deleted_text,
                                                     prev_delete.deleted_text)
                prev_delete.start = undo_action.start
            self.undo_stack.append(prev_delete)
        else:
            self.undo_stack.append(prev_delete)
            self.undo_stack.append(undo_action)
        self.modified = True

    def on_begin_user_action(self, *args, **kwargs):
        pass

    def begin_not_undoable_action(self):
        """don't record the next actions
        
        toggles self.not_undoable_action"""
        self.not_undoable_action = True        

    def end_not_undoable_action(self):
        """record next actions
        
        toggles self.not_undoable_action"""
        self.not_undoable_action = False
    
    def undo(self):
        """undo inserts or deletions

        undone actions are being moved to redo stack"""
        if not self.undo_stack:
            return
        self.begin_not_undoable_action()
        self.undo_in_progress = True
        undo_action = self.undo_stack.pop()
        self.redo_stack.append(undo_action)
        if isinstance(undo_action, UndoableInsert):
            start = self.get_iter_at_offset(undo_action.offset)
            stop = self.get_iter_at_offset(
                undo_action.offset + undo_action.length
            )
            self.delete(start, stop)
            self.place_cursor(start)
        else:
            start = self.get_iter_at_offset(undo_action.start)
            stop = self.get_iter_at_offset(undo_action.end)
            self.insert(start, undo_action.deleted_text)
            if undo_action.delete_key_used:
                self.place_cursor(start)
            else:
                self.place_cursor(stop)
        self.end_not_undoable_action()
        self.undo_in_progress = False
        self.modified = True

    def redo(self):
        """redo inserts or deletions

        redone actions are moved to undo stack"""
        if not self.redo_stack:
            return
        self.begin_not_undoable_action()
        self.undo_in_progress = True
        redo_action = self.redo_stack.pop()
        self.undo_stack.append(redo_action)
        if isinstance(redo_action, UndoableInsert):
            start = self.get_iter_at_offset(redo_action.offset)
            self.insert(start, redo_action.text)
            new_cursor_pos = self.get_iter_at_offset(
                redo_action.offset + redo_action.length
            )
            self.place_cursor(new_cursor_pos)
        else:
            start = self.get_iter_at_offset(redo_action.start)
            stop = self.get_iter_at_offset(redo_action.end)
            self.delete(start, stop)
            self.place_cursor(start)
        self.end_not_undoable_action()
        self.undo_in_progress = False
        self.modified = True


    ## Passthrus until we can encapsulate TextBuffer fully
    def place_cursor(self, *args, **kwargs):
        self.text_buffer.place_cursor(*args, **kwargs)

    def set_text(self, *args, **kwargs):
        self.text_buffer.set_text(*args, **kwargs)

    def get_text(self, *args, **kwargs):
        return self.text_buffer.get_text(*args, **kwargs)

    def get_end_iter(self, *args, **kwargs):
        return self.text_buffer.get_end_iter(*args, **kwargs)

    def get_insert(self, *args, **kwargs):
        return self.text_buffer.get_insert(*args, **kwargs)

    def get_char_count(self, *args, **kwargs):
        return self.text_buffer.get_char_count(*args, **kwargs)

    def get_start_iter(self, *args, **kwargs):
        return self.text_buffer.get_start_iter(*args, **kwargs)

    def get_line_count(self, *args, **kwargs):
        return self.text_buffer.get_line_count(*args, **kwargs)

    def get_end_iter(self, *args, **kwargs):
        return self.text_buffer.get_end_iter(*args, **kwargs)



