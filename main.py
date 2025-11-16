import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user.name}")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=f"debates in {len(bot.guilds)} servers"
    ))
    print("🔄 Syncing slash commands...")
    await bot.tree.sync()
    print("✅ Slash commands synced.")

async def main():
    async with bot:
        await bot.load_extension("cogs.debate")
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
