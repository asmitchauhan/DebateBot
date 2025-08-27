import discord
from discord.ext import commands
from discord import app_commands
import openai
import re

class DebateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessions = {}

        # ✅ DeepSeek (via OpenRouter)
        openai.api_key = "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"
        openai.api_base = "https://openrouter.ai/api/v1"

    @app_commands.command(name="start", description="Start a debate with multiple users and a topic.")
    @app_commands.describe(
        debaters="Mention users separated by commas (e.g. @user1, @user2, @user3)",
        topic="Topic of the debate (e.g. 'Is capitalism better than socialism?')"
    )
    async def start(self, interaction: discord.Interaction, debaters: str, topic: str):
        if interaction.channel.id in self.sessions:
            await interaction.response.send_message("❌ A debate is already running in this channel.", ephemeral=True)
            return

        members = []
        for mention in debaters.split(','):
            mention = mention.strip()
            if mention.startswith("<@") and mention.endswith(">"):
                mention = mention.replace("<@", "").replace("!", "").replace(">", "")
            try:
                member = await interaction.guild.fetch_member(int(mention))
                members.append(member)
            except:
                continue

        if len(members) < 2:
            await interaction.response.send_message("❌ Please mention at least two valid users.", ephemeral=True)
            return

        self.sessions[interaction.channel.id] = {
            "users": {m.id for m in members},
            "names": {m.id: m.display_name for m in members},
            "topic": topic,
            "log": []
        }

        await interaction.response.send_message(
            f"🧠 Debate started between: " + ", ".join([f"**{m.display_name}**" for m in members]) +
            f"\n📌 **Topic:** {topic}\nUse `/stop` to end and get the result."
        )

    @app_commands.command(name="stop", description="Stop and analyze the current debate.")
    async def stop(self, interaction: discord.Interaction):
        channel_id = interaction.channel.id
        if channel_id not in self.sessions:
            await interaction.response.send_message("❌ No active debate in this channel.", ephemeral=True)
            return

        session = self.sessions.pop(channel_id)
        log = session["log"]
        if not log:
            await interaction.response.send_message("⚠️ No messages recorded.")
            return

        topic = session["topic"]
        debate_text = "\n".join(log)
        await interaction.response.send_message("🧠 Analyzing the debate...")

        participants = list(session['names'].values())

        prompt = f"""
You are a fair and unbiased AI debate judge. Analyze the following multi-person debate between {', '.join(participants)}.

📌 Topic: {topic}

Return the result in this format:
- Score for <DebaterName>: <score>
- Winner: <best debater name>
- Reason:

Debate:
{debate_text}
"""

        try:
            response = openai.ChatCompletion.create(
                model="deepseek/deepseek-r1",
                messages=[{"role": "user", "content": prompt}]
            )
            result = response["choices"][0]["message"]["content"]
            await interaction.followup.send(f"🧾 **Judgment Result:**\n{result}")
        except Exception as e:
            await interaction.followup.send(f"❌ DeepSeek error:\n```{e}```")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        session = self.sessions.get(message.channel.id)
        if session and message.author.id in session["users"]:
            speaker = session["names"][message.author.id]
            session["log"].append(f"{speaker}: {message.content}")

async def setup(bot):
    await bot.add_cog(DebateCog(bot))
