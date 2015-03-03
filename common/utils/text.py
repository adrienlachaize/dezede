# coding: utf-8

from __future__ import unicode_literals
from django.utils import six

from django.utils.encoding import smart_text
from django.utils.functional import lazy
from django.utils.translation import pgettext, ugettext_lazy as _


def remove_windows_newlines(text):
    return text.replace('\r\n', '\n').replace('\r', '\n')


def capfirst(text):
    out = smart_text(text)
    if not out:
        return out
    return out[0].upper() + out[1:]


def str_list(iterable, infix=None, last_infix=None):
    """
    Concatène une liste de chaîne de caractères avec des virgules.

    >>> l = ['Jeanne', 'Lola', 'Perrine', 'Marion']
    >>> print(str_list(l))
    Jeanne, Lola, Perrine, Marion
    """

    if infix is None:
        infix = pgettext('infix d’une liste', ', ')

    l = [e for e in iterable if e]

    if last_infix is None:
        return infix.join(l)

    suffix = ''
    if len(l) > 1:
        suffix = last_infix + l.pop()
    return infix.join(l) + suffix


def str_list_w_last(iterable, infix=None, last_infix=None,
                    oxfordian_last_infix=None, oxford_comma=True):
    """
    Concatène une liste de chaîne de caractères avec des virgules
    et un «,\u00A0et\u00A0» final («\u00A0et\u00A0» pour deux éléments).
    Pour désactiver la virgule d’Oxford, passer oxford_comma=False en argument.

    >>> l = ['Jeanne', 'Marion', 'Lola', 'Perrine']
    >>> print(str_list_w_last(l))
    Jeanne, Marion, Lola et\u00A0Perrine
    >>> print(str_list_w_last(l[:2]))
    Jeanne et\u00A0Marion
    """

    l = [e for e in iterable if e]

    if infix is None:
        infix = pgettext('infix d’une liste', ', ')

    if oxford_comma and len(l) > 2:
        if oxfordian_last_infix is None:
            oxfordian_last_infix = pgettext(
                'dernier infix pour plus de 2 éléments', ' et ')
        last_infix = oxfordian_last_infix
    elif last_infix is None:
        last_infix = pgettext('dernier infix pour 2 éléments', ' et ')

    return str_list(l, infix, last_infix)


def ex(txt, pre='', post=''):
    """
    >>> print(ex('30/01/1989'))
    Exemple : « 30/01/1989 ».
    """
    return _('Exemple : %(pre)s« %(txt)s »%(post)s.') % {
        'pre': pre,
        'txt': txt,
        'post': post,
    }
ex = lazy(ex, six.text_type)