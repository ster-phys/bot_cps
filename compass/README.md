# compass

A library for easy handling of Compass data.
The main items provided by this library are cards, heroes and stages.

## Quick Example

Before looking at the examples, keep in mind the followings.

The data provided by this library are available as `compass.CardData`, `compass.HeroData` and `compass.StageData`, which is a list of `compass.Card` class, a list of `compass.Hero` class and a list of `compass.Stage` class, respectively.

In addition, to use this library, need a key to decrypt the data. The key must be registered in the environment variable `BOT_CPS_TOKEN`.

- `compass.Card`, `compass.CardData` example

```python
>>> from compass import CardData
>>> cd = CardData()
>>> len(cd)
415
>>> cd.get_card("UR", normal=False, collabo=True)
Card(_Card__name=【NieR:Automata】戦いの始まり, _Card__rarity=<Rarity.UR: 'ur'>, ...)
>>> cd.get_card("UR", normal=False, collabo=True).generate_image()
'/tmp/tmpyipji4qe.png'
>>> cd["全天"]
Card(_Card__name=全天首都防壁 Hum-Sphere LLIK, _Card__rarity=<Rarity.UR: 'ur'>, ...)
```

For details, check the implementation.

## Data Updating

The data will be updated manually using [Github Actions](https://github.com/ster-phys/bot_cps/actions).
