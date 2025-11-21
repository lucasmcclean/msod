import os
from typing import Final

import discord
import httpx
from discord import app_commands

TOKEN: Final[str] = os.getenv("DISCORD_TOKEN", "uh oh")
GUILD_ID: Final[int] = int(os.getenv("DISCORD_GUILD_ID", "whoops"))

START_URL: Final[str] = os.getenv("START_API_URL", "oh no")
STOP_URL: Final[str] = os.getenv("STOP_API_URL", "not this too")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


async def invoke_lambda(url: str) -> str:
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url)
        resp.raise_for_status()
        return resp.text


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user}")
    await tree.sync(guild=discord.Object(id=GUILD_ID))


@tree.command(
    name="start",
    description="Start the server",
    guild=discord.Object(id=GUILD_ID),
)
async def mc_start(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Starting server…")
    result = await invoke_lambda(START_URL)
    await interaction.followup.send(f"```json\n{result}\n```")


@tree.command(
    name="stop",
    description="Stop the server",
    guild=discord.Object(id=GUILD_ID),
)
async def mc_stop(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Stopping server…")
    result = await invoke_lambda(STOP_URL)
    await interaction.followup.send(f"```json\n{result}\n```")


bot.run(TOKEN)
