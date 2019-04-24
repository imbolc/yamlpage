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
    ...     ('body|md', '- foo\n- bar'),
    ... ))

    >>> path = './content/^my^url.yaml'
    >>> content = open(path).read()
    >>> print(content)
    title: foo
    body|md: |-
        - foo
        - bar
    <BLANKLINE>


Get page

    >>> p.get(url) == {'body|md': '- foo\n- bar', 'title': 'foo'}
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


Filters
-------
You can automaticaly apply filters to a particular page fields.
As an example let's render `body` markdown to html.

>>> import misaka
>>> p = YamlPage('./content', filters={"md": misaka.html})
>>> p.get(url)["body"] == '<ul>\n<li>foo</li>\n<li>bar</li>\n</ul>\n'
True