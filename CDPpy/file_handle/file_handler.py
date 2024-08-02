from .reader import DEFAULT_READER

class FileHandler:
    def __init__(self, file, reader=DEFAULT_READER) -> None:
        self._file = file
        self._reader = reader

    def read(self):
        return self._reader.read(self._file)