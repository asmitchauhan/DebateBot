import discord
from discord.ext import commands
from discord import app_commands

class HelloCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Says hello!")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello, {interaction.user.name}!")

    # Optional: auto-sync when bot joins a new guild (rarely needed)
    async def cog_load(self):
        await self.bot.tree.sync()

async def setup(bot):
    await bot.add_cog(HelloCog(bot))
