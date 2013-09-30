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

    >>> path = './content/#my#url.yml'
    >>> print open(path).read()
    title: foo
    body: |-
      foo
      bar
    <BLANKLINE>


Get page

    >>> p.get(url)
    {'body': 'foo\nbar', 'title': 'foo'}

    >>> p.get('/not/found/') is None
    True