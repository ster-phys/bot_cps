"""
Compass Data Structures
~~~~~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2021-present ster
:license: GPL-3.0, see LICENSE for more details.

"""

__title__ = "compass"
__author__ = "ster"
__license__ = "GPL-3.0"
__copyright__ = "Copyright 2021-present ster"
__version__ = "1.1.2"

__all__ = (
    "Activation",
    "Attribute",
    "Card",
    "CardData",
    "Collabo",
    "Hero",
    "HeroData",
    "Locale",
    "Parameter",
    "Rank",
    "Rarity",
    "Role",
    "Stage",
    "StageData",
    "Status",
    "Tstr",
    "similar",
    "translator",
)


from .activation import Activation
from .attribute import Attribute
from .card import Card
from .collabo import Collabo
from .data import CardData, HeroData, StageData
from .hero import Hero
from .rank import Rank
from .rarity import Rarity
from .role import Role
from .stage import Stage
from .status import Parameter, Status
from .utils import Locale, Tstr, similar, translator
