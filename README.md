yamlpage
========
Flatpages based on files with yaml syntax

Install
-------
    pip install yamlpage

Usage
-----
    >>> from yamlpage import YamlPage
    >>> p = YamlPage('./content')


Put page

    >>> url = '/my/url'
    >>> p.put(url, (
    ...     ('title', 'foo'),
    ...     ('body', 'foo\nbar'),
    ... ))

    >>> path = './content/^my^url.yaml'
    >>> print(open(path).read())
    title: foo
    body: |-
      foo
      bar
    <BLANKLINE>


Get page

    >>> p.get(url) == {'key': '/my/url', 'body': 'foo\nbar', 'title': 'foo'}
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

    >>> p = YamlPage('./content', backend=MultiFolderBackend)
    >>> p.put('multi/folder/backend', 'data')
    >>> os.path.exists('./content/multi/folder/backend.yaml')
    True