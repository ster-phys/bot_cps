"""
A library that provides Compass Data Structures

The GNU General Public License v3.0 (GPL-3.0)

Copyright (C) 2021-present ster <ster.physics@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

"""

from __future__ import annotations

__all__ = (
    "similar",
    "translator",
)


from typing import Any, Callable, NewType

from Levenshtein import jaro_winkler
from pykakasi import kakasi

TRANS_TABLE = str.maketrans({
    " ": "",
    "　": "",
    "＆": "&",
    "！": "!",
    "（": "(",
    "）": ")",
    "＊": "∗",
    "＃": "#",
    "-": "",
    "＝": "=",
    "／": "",
    "/": "",
    "㌍": "カロリー",
    "［": "[",
    "］": "]",
    ";": "",
    "-": "",
    "―": "",
})


def translator(text: str) -> str:
    """Converts ``text`` according to :attr:`~TRANS_TABLE`.

    Parameters
    ----------
    text: :class:`str`
        Target string to be translated.

    Returns
    -------
    Translated strings using :attr:`~TRANS_TABLE`.

    """
    return text.translate(TRANS_TABLE)


# pykakasi settings
_kakasi = kakasi()
_kakasi.setMode("a", "H")
_kakasi.setMode("K", "H")
_kakasi.setMode("J", "H")
_kakasi = _kakasi.getConverter()
_kakasi: Callable[[str], str] = _kakasi.do


SeqElement = NewType("SeqElement", list[Any])


def similar(word: str, target: list[SeqElement],
            key: Callable[[SeqElement], list[str]] = lambda el: el) -> SeqElement:
    """Gets an element of ``target`` containing a string similar to ``word``.

    Parameters
    ----------
    word: :class:`str`
        Words to search for.
    target: List[:class:`SeqElement`]
        Sequence containing the search target.
    key: Callable[[:class:`SeqElement`], List[:class:`str`]]
        Function to get an object of the same type (:class:`str`) as the search
        target from elements of ``target``.

    Returns
    -------
    :class:`SeqElement`
        An element of ``target`` that contains the string the most similar to ``word``.

    """

    def get_elements(seq_element: SeqElement) -> list[str]:
        return list(map(lambda el: translator(_kakasi(el)), key(seq_element)))

    words_list: list[list[str]] = []
    for el in target:
        words_list.append(get_elements(el))

    word = translator(_kakasi(word))

    for words in words_list:
        if word in words:
            return target[words_list.index(words)]

    jaro_list = []
    for words in words_list:
        dist_list = []
        for el in words:
            dist_list.append(jaro_winkler(word, el))
        jaro_list.append(max(dist_list))

    return target[jaro_list.index(max(jaro_list))]
