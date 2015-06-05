import shelve


class Session(object):
    def add_open_filename(self, filename):
        raise NotImplementedError("Please Implement this method")

    def remove_open_filename(self, filename):
        raise NotImplementedError("Please Implement this method")

    def get_open_filenames(self):
        """
        :return: []
        """
        raise NotImplementedError("Please Implement this method")

    def clear(self):
        raise NotImplementedError("Please Implement this method")


class FileStoreSession(Session):

    file_list_key = 'open_filenames'

    def __init__(self, filepath):
        self.filenames = []
        self.shelve_filepath = filepath
        self.shelf = shelve.open(self.shelve_filepath)
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


class PrivateSession(Session):
    def remove_open_filename(self, filename):
        pass

    def clear(self):
        pass

    def add_open_filename(self, filename):
        pass

    def get_open_filenames(self):
        return []
        pass