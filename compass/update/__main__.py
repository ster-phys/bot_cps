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

import sys
from os.path import abspath, dirname

sys.path.append(dirname(dirname(abspath(__file__))))


import logging

format = "%(asctime)s : %(levelname)s - %(filename)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=format)


import asyncio
from argparse import ArgumentParser, Namespace

import card
import hero


def get_option() -> Namespace:
    argparser = ArgumentParser()
    argparser.add_argument("name", type=str, help="updates target, card or hero")
    argparser.add_argument("url", type=str, help="url of Yagi Simulator")
    argparser.add_argument("token", type=str, help="fernet key")
    return argparser.parse_args()

if __name__ == "__main__":
    args = get_option()

    if args.name == "card":
        asyncio.run(card.__main__(args.url, args.token))
    elif args.name == "hero":
        asyncio.run(hero.__main__(args.url, args.token))
