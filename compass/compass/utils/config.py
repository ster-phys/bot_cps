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
    "CONFIG",
)


class _Config(object):
    class _Size(object):
        @property
        def ICON(self) -> tuple[int, int]:
            """Hero icon size."""
            return (122, 122)

        @property
        def HERO(self) -> tuple[int, int]:
            """Hero image size."""
            return (161, 161)

        @property
        def CARD(self) -> tuple[int, int]:
            """Card image size."""
            return (180, 250)

        @property
        def STAGE(self) -> tuple[int, int]:
            """Stage image size."""
            return (736, 276)

    SIZE = _Size()

CONFIG = _Config()
