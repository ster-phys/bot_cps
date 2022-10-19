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

__all__ = (
    "Collabo",
)


from enum import Enum


class Collabo(str, Enum):
    """Names of collaboration held in Compass."""
    NONE = ""
    EX = "エナ缶"

    BL = "BEATLESS"
    BUNSUTO = "文豪ストレイドッグス"
    DANMACHI = "ダンまち"
    DANRON = "ダンガンロンパ"
    FATE = "fate"
    FF = "ファイナルファンタジーXV"
    GG = "ギルティギア"
    GG2 = "ギルティギア追加"
    HAKKA = "ハッカドール"
    KABUKI = "超歌舞伎×千本桜"
    KONOSUBA = "この素晴らしい世界に祝福を!"
    KYOJIN = "進撃の巨人"
    MIKU = "初音ミク"
    MIKU2 = "鏡音リン・レン"
    NA = "NieR:Automata"
    NEKOMIYA = "猫宮ひなた"
    OL = "オーバーロード"
    P5 = "ペルソナ5"
    REF = "THE REFLECTION"
    REZERO = "Re:ゼロから始める異世界生活"
    RYZA = "ライザのアトリエ2"
    SAO = "ソードアートオンライン"
    SATSUTEN = "殺戮の天使"
    SF = "ストリートファイターV"
    SG = "STEINS;GATE"
    TENSURA = "転生したらスライムだった件"

    def __str__(self) -> str:
        return self.value
