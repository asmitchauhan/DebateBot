import discord
from discord.ext import commands

TOKEN = "MTM4ODc0NjUyNTYxNzY4ODY1Nw.GtHm83.qk6YJVwZIOy5jJaXXovoer-XJwATSXiQZm2q-E"

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
    await bot.load_extension("cogs.hello")
    await bot.load_extension("cogs.debate")  # ← Add debate Cog here

bot.run(TOKEN)
