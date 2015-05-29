import shelve


class Session(object):

    file_list_key = 'open_filenames'
    shelve_filename = '/tmp/pyroom.session.tmpfile'

    def __init__(self):
        self.filenames = []
        self.shelf = shelve.open(self.shelve_filename)
        if self.shelf.get(self.file_list_key) is None:
            self.shelf[self.file_list_key] = []

    def add_open_filename(self, filename):
        file_list = self.shelf.get(self.file_list_key)
        file_list.append(filename)
        self.shelf[self.file_list_key] = file_list
        self.shelf.sync()

    def remove_open_filename(self, filename):
        if filename in self.get_open_filenames():
            file_list = self.get_open_filenames()
            file_list.remove(filename)
            self.shelf[self.file_list_key] = file_list
            self.shelf.sync()

    def get_open_filenames(self):
        return self.shelf.get(self.file_list_key)

    def clear(self):
        self.shelf[self.file_list_key] = []
