# bot_cps

A library describing cogs for Compass bot.

This library mainly depends on [discord.py](https://github.com/Rapptz/discord.py).
Therefore, if you have created bots with [discord.py](https://github.com/Rapptz/discord.py), you can load this cog and include some features.

**Only python3.10 is supported.**

## Quick Example

### Launch Immediately

If you do not introduce this into an existing bot or customise the cog to be loaded, you can launch it as follows.

1. Accesses the [Discord Developer Portal](https://discord.com/developers) to obtain a token for your bot.
2. Loads the token as the environment variable `DISCORD_TOKEN`.
3. Obtains the ID of the server using the bot from the app and loads it as the environment variable `BOT_CPS_GUILD_ID`.
4. Clones this repository and runs `$ cd bot_cps`.
5. Runs `$ pip install -r requirements.txt`.
6. Runs `$ python3.10 bot_cps`.

Note: Some features that depend on [Compass library](../compass/README.md) require a decryption key.

### Customise

The cogs provided by this library can be obtained from `bot_cps.EXTENSIONS`.
Loads only the cogs you need and uses them.
