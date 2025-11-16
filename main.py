import discord
from discord.ext import commands

TOKEN = "MTQzOTU3NTgyNzk4MDQ4NDc0MA.GBfddh.em3tKj4AHD_qTPPhUPHOuXLA3c8xYUNzciCIyw"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=f"debates in {len(bot.guilds)} servers"
    ))
    await bot.tree.sync()
    print("✅ Synced slash commands.")

@bot.event
async def setup_hook():
    await bot.load_extension("cogs.debate")

bot.run(TOKEN)
