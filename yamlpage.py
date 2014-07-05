# -*- coding: utf-8 -*-
'''
yamlpage
========
Flatpages based on files with yaml syntax

Install
-------
    pip install yamlpage

Usage
-----
    >>> import os
    >>> from yamlpage import YamlPage
    >>> p = YamlPage('./content')


Put page

    >>> url = '/my/url'
    >>> p.put(url, (
    ...     ('title', 'foo'),
    ...     ('body', 'foo\\nbar'),
    ... ))

    >>> path = './content/^my^url.yaml'
    >>> print(open(path).read())
    title: foo
    body: |-
        foo
        bar
    <BLANKLINE>


Get page

    >>> p.get(url) == {'key': '/my/url', 'body': 'foo\\nbar', 'title': 'foo'}
    True

    >>> p.get('/not/found/') is None
    True

Check if page exists

    >>> p.exists(url)
    True
    >>> p.exists('/not/found/')
    False


Built in backends
-----------------
SingleFolderBackend (default) maps 'my/url' to filename 'my^url.yaml'

    >>> p = YamlPage('./content')
    >>> p.put('single/folder/backend', 'data')
    >>> os.path.exists('./content/single^folder^backend.yaml')
    True

MultiFolderBackend maps 'my/url' to filename 'my/url.yaml'

    >>> p = YamlPage('./content', backend='MultiFolderBackend')
    >>> p.put('multi/folder/backend', 'data')
    >>> os.path.exists('./content/multi/folder/backend.yaml')
    True
'''
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import warnings
import importlib

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    warnings.warn('You have to install libyaml and reinstall pyyaml '
                  'for increase perfomance')
    from yaml import Loader
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


if sys.version_info > (3, ):
    unicode = str
    basestring = str


class FileSystemBackend(object):
    '''Parent for file system based backends'''
    def __init__(self, root_dir='.', file_extension='yaml'):
        self.root_dir = root_dir
        self.file_extension = '.' + file_extension.lstrip('.')

    def _key_to_path(self, key):
        raise Exception('This method should be overridden')

    def exists(self, key):
        path = self._key_to_path(key)
        return os.path.isfile(path)

    def get(self, key):
        path = self._key_to_path(key)
        try:
            with open(path, 'rb') as f:
                return f.read().decode('utf-8')
        except (IOError, UnicodeDecodeError):
            pass

    def put(self, key, content):
        path = self._key_to_path(key)
        dirname = os.path.dirname(path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        with open(path, 'w') as f:
            f.write(content)


class SingleFolderBackend(FileSystemBackend):
    '''
        >>> backend = SingleFolderBackend('./content/')
        >>> backend.get('my/url')
        >>> backend.exists('my/url')
        False
        >>> os.path.exists('./content/my^url.yaml')
        False
        >>> backend.put('my/url', 'data')
        >>> os.path.exists('./content/my^url.yaml')
        True
        >>> backend.exists('my/url')
        True
        >>> backend.get('my/url') == 'data'
        True
    '''
    def __init__(self, root_dir='.', file_extension='yaml',
                 path_delimiter='^'):
        super(SingleFolderBackend, self).__init__(root_dir, file_extension)
        self.path_delimiter = path_delimiter

    def _key_to_path(self, key):
        '''
            >>> backend = SingleFolderBackend('root/dir')
            >>> backend._key_to_path('a/b/c')
            'root/dir/a^b^c.yaml'
        '''
        path = key.replace('/', self.path_delimiter) + self.file_extension
        return os.path.join(self.root_dir, path)


class MultiFolderBackend(FileSystemBackend):
    '''
        >>> backend = MultiFolderBackend('./content/')
        >>> backend.get('my/url')
        >>> backend.exists('my/url')
        False
        >>> os.path.exists('./content/my/url.yaml')
        False
        >>> backend.put('my/url', 'data')
        >>> os.path.exists('./content/my/url.yaml')
        True
        >>> backend.exists('my/url')
        True
        >>> backend.get('my/url') == 'data'
        True
    '''
    def _key_to_path(self, key):
        '''
            >>> backend = MultiFolderBackend('root/dir')
            >>> backend._key_to_path('a/b/c')
            'root/dir/a/b/c.yaml'
            >>> backend._key_to_path('/a/b/c/')
            'root/dir/a/b/c.yaml'
            >>> backend._key_to_path('../../../a/b/c')
            'root/dir/a/b/c.yaml'
        '''
        path = os.path.normpath(key).lstrip('./')
        return os.path.join(self.root_dir, path) + self.file_extension


class YamlPage(object):
    def __init__(self, *args, **kwargs):
        backend = kwargs.pop('backend', 'SingleFolderBackend')
        backend_class = get_object_by_name(backend)
        if not backend_class:
            raise Exception('Unknown backend: %s' % backend)
        self.backend = backend_class(*args, **kwargs)

    def exists(self, key):
        return self.backend.exists(key)

    def get(self, key):
        '''Return loaded yaml or None'''
        dump = self.backend.get(key)
        if dump:
            page = yaml.load(dump, Loader=Loader)
            page.setdefault('key', key)
            return page

    def put(self, key, data):
        dump = dumps(data)
        self.backend.put(key, dump)


class literal(unicode):
    pass


class unquoted(unicode):
    pass


def ordered_dict_presenter(dumper, data):
    return dumper.represent_dict(data.items())


def literal_presenter(dumper, data):
    return dumper.represent_scalar(
        'tag:yaml.org,2002:str', data, style='|')


def unquoted_presenter(dumper, data):
    return dumper.represent_scalar(
        'tag:yaml.org,2002:str', data, style='')

yaml.add_representer(literal, literal_presenter)
yaml.add_representer(OrderedDict, ordered_dict_presenter)
yaml.add_representer(unquoted, unquoted_presenter)


def dumps(items):
    '''
    Tip: if you want to do literal (|) style of strings, remove trailing spaces

        >>> dumps([1, 2, 3])
        '- 1\\n- 2\\n- 3\\n'

        >>> print(dumps([('foo', 1), ('bar', 2)]))
        foo: 1
        bar: 2
        <BLANKLINE>

        >>> print(dumps({'foo': 1, 'bar': 2}))
        bar: 2
        foo: 1
        <BLANKLINE>
    '''
    if isinstance(items, dict):
        items = sorted(items.items(), key=lambda x: x[0])
    try:
        dict(items)
    except (TypeError, ValueError):
        data = items
    else:
        data = OrderedDict()
        for k, v in items:
            if isinstance(v, basestring):
                if '\n' in v:
                    v = v.replace('\r', '')
                    v = v.replace('\t', '    ')
                    # literal string doesn't works
                    # if any of string has trailing space
                    v = '\n'.join(r.rstrip() for r in v.split('\n'))
                    v = literal(v)
                else:
                    v = unquoted(v)
            data[k] = v
    return yaml.dump(data, allow_unicode=True, default_flow_style=False,
                     indent=4)


def get_object_by_name(name):
    '''
        >>> dirname = get_object_by_name('os.path.dirname')
        >>> dirname == os.path.dirname
        True
    '''
    if not isinstance(name, basestring):
        return name
    if '.' not in name:
        return globals().get(name)
    modname, attrname = name.rsplit('.', 1)
    module = importlib.import_module(modname)
    return getattr(module, attrname, None)


if __name__ == '__main__':
    import shutil
    import doctest

    content_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'content')
    shutil.rmtree(content_dir, ignore_errors=True)
    os.makedirs(content_dir)

    print(doctest.testmod(
        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE
    ))
