import csv
import enum
import gzip
import json
import os
import os.path
import pickle
import shutil


BASE_DIRPATH = 'cache'


class Format(enum.Enum):
    TEXT = 0
    JSON = 1
    CSV = 2
    PICKLE = 3


# TODO: Restore from backups?
class Cache:
    def __init__(
        self,
        path,
        format=Format.TEXT,
    ):
        self.path = path
        self.format = format
        
        self.data = None

    @property
    def backup_path(self):
        return self.path + '.bak.gz'

    def load(self):
        if self.data is not None:
            return

        if self.format == Format.TEXT:
            with open(self.path) as f:
                self.data = f.read()
        elif self.format == Format.JSON:
            with open(self.path) as f:
                self.data = json.load(f)
        elif self.format == Format.CSV:
            with open(self.path, encoding='latin-1') as f:
                reader = csv.reader(f, delimiter=',', quotechar='"')
                self.data = list(reader)
        elif self.format == Format.PICKLE:
            with open(self.path, 'rb') as f:
                self.data = pickle.load(f)

    def reload(self):
        self.data = None
        self.load()

    def save(self):
        if self.data is None:
            return

        tmp_path = self.path + '.tmp'
        try:
            if self.format == Format.TEXT:
                with open(tmp_path, 'w') as f:
                    f.write(self.data)
            elif self.format == Format.JSON:
                with open(tmp_path, 'w') as f:
                    json.dump(self.data, f, indent=4)
            elif self.format == Format.CSV:
                with open(tmp_path, 'w') as f:
                    writer = csv.writer(f, delimiter=',', quotechar='"')
                    writer.writerows(self.data)
            elif self.format == Format.PICKLE:
                with open(tmp_path, 'wb') as f:
                    pickle.dump(self.data, f)
        except:
            try:
                os.remove(tmp_path)
            except:
                pass
            raise

        os.rename(tmp_path, self.path)

    def back_up(self):
        with open(self.path, 'rb') as f:
            data = f.read()

        data = gzip.compress(data)

        tmp_path = self.backup_path + '.tmp'
        try:
            with open(tmp_path, 'wb') as f:
                f.write(data)
        except:
            try:
                os.remove(tmp_path)
            except:
                pass
            raise

        os.rename(tmp_path, self.backup_path)


class SplitCache:
    def __init__(
        self,
        path,
        format=Format.TEXT,
    ):
        self.path = path
        self.format = format

        self.pieces = None
        self.data = None

    @property
    def backup_path(self):
        return self.path + '.bak'

    @property
    def backup_archive_path(self):
        return self.path + '.bak'

    def load_pieces(self):
        if self.pieces is not None:
            return
        self.pieces = {}

        dirpath, _, filenames = next(os.walk(self.path), (None, None, []))
        if not filenames:
            return
        filenames = set(filenames)

        for filename in filenames - self.pieces.keys():
            filepath = os.path.join(dirpath, filename)
            cache = Cache(filepath, format=self.format)
            self.pieces[filename] = cache

        for filename in self.pieces.keys() - filenames:
            del self.pieces[filename]

    def reload_pieces(self):
        self.pieces = None
        self.data = None
        self.load_pieces()

    def load_all(self):
        if self.data is not None:
            return

        self.load_pieces()
        self.data = {}
        for name, piece in self.pieces.items():
            piece.load()
            self.data[name] = piece.data

    def reload_all(self):
        self.reload_pieces()
        self.data = {}
        for name, piece in self.pieces.items():
            piece.reload()
            self.data[name] = piece.data

    def _create_piece(self, name):
        filepath = os.path.join(self.path, name)
        cache = Cache(filepath, format=self.format)
        self.pieces[name] = cache
        cache.data = self.data[name]

    def save_all(self):
        if self.pieces is None:
            return

        for name in self.data.keys() - self.pieces.keys():
            self._create_piece(name)

        for piece in self.pieces.values():
            piece.save()

    def load(self, name=None):
        if name is None:
            self.load_all()
        else:
            self.pieces[name].load()

    def reload(self, name=None):
        if name is None:
            self.reload_all()
        else:
            self.pieces[name].reload()

    def save(self, name=None):
        if name is None:
            self.save_all()
        else:
            if name not in self.pieces:
                self._create_piece(name)
            self.pieces[name].save()

    def back_up(self):
        shutil.make_archive(self.backup_path, 'gztar', self.path)
