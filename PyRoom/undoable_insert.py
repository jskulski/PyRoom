class UndoableInsert(object):
    """something that has been inserted into our textbuffer"""
    def __init__(self, text_iter, text, length):
        self.offset = text_iter.get_offset()
        self.text = text
        self.length = length
        if self.length > 1 or self.text in ("\r", "\n", " "):
            self.mergeable = False
        else:
            self.mergeable = True
