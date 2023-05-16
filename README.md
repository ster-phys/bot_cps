# <img src="./icons/bot_cps.png" width="32px" align="center"> bot_cps

[In Japanese](./README.ja.md)

[![python3.10](https://img.shields.io/badge/python-3.10-3776AB.svg?logo=python)](https://docs.python.org/3.10/) [![LICENSE](https://img.shields.io/github/license/ster-phys/bot_cps)](./LICENSE) [![Discord](https://img.shields.io/discord/834671256367530014.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](http://discord.gg/Pmt5BetUqb) [![Twitter Follow](https://img.shields.io/twitter/follow/bot_cps?style=social)](https://twitter.com/bot_cps)

This repository is a [Discord](https://discord.com/) bot for [#compass](https://app.nhn-playart.com/compass/), written in python.
We provide a variety of features.

This mainly depends on [discord.py](https://github.com/Rapptz/discord.py).
Therefore, if you have created bots with [discord.py](https://github.com/Rapptz/discord.py), you can load this cog and include some features.

This also depends on [ster-phys/compass](https://github.com/ster-phys/compass) repository.

## How To Use

If you want to just use the bot, please click on [the link](https://discord.com/api/oauth2/authorize?client_id=776010907373010954&permissions=1074055168&scope=bot%20applications.commands) to install it.

If you want to use a self-hosted bot, do the following.

```shell
python3.10 -m pip install "bot_cps@git+https://github.com/ster-phys/bot_cps.git"
export DISCORD_TOKEN=YOUR_BOT_TOKEN # Obtain from Developer Portal
python3.10 -m bot_cps --local your_guild_id
```

Or, if you want to add some of this bot's `cog`s, you can obtain from `bot_cps.extensions`.

```python
import bot_cps
print(bot_cps.extensions)
```

## Support Us

If you would like to support us, please use the following link :)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/bot.cps)

## For Developers and Users

The first commit was made on Tue Nov 17 2020 18:45:20 GMT+0900.
Over the next two years, 958 commits were made and `bot_cps` repository evolved.

The history of its development should be kept intact, but it contains many unnecessary commits, inaccurate commit messages, etc., which make it a useless commit.
Therefore, I decided to keep only the first commit, which records the beginning of `bot_cps`, and force the other commits to be overwritten to make the git repository lighter and to clarify its history.

Although the number of commits are few, it would be nice to bear in mind that the program as it exists today is the result of a great deal of effort :)

2022-10-18

ster @ster-phys

## Memorandum

The bots are launched in the following ways.

First, clone the required directory.

```shell
mkdir apps && cd apps
git init
git config core.sparseCheckout true
git remote add origin git@github.com:ster-phys/bot_cps.git
echo apps >> .git/info/sparse-checkout
git pull origin master
```

Install the necessary libraries and launch the bot.

```shell
python3.10 -m pip install "bot_cps@git+https://github.com/ster-phys/bot_cps.git"
DISCORD_TOKEN=ASHLEY_BOT_TOKEN python3.10 -m apps.ashley &
DISCORD_TOKEN=MAILOT_BOT_TOKEN python3.10 -m apps.mailot &
DISCORD_TOKEN=MAIN_BOT_TOKEN python3.10 -m apps.main &
```
