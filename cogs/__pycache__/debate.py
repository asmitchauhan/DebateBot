import discord
from discord.ext import commands
from discord import app_commands
import openai
import os
from dotenv import load_dotenv

class DebateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessions = {}

        # Load OpenRouter API settings
        load_dotenv()
        openai.api_key = os.getenv("OPENROUTER_API_KEY")
        openai.api_base = os.getenv("OPENROUTER_API_BASE")

    # ------------ START COMMAND ------------
    @app_commands.command(name="start", description="Start a debate with multiple users and a topic.")
    @app_commands.describe(
        debaters="Tag users separated by commas (@user1, @user2, @user3)",
        topic="Debate topic"
    )
    async def start(self, interaction: discord.Interaction, debaters: str, topic: str):

        if interaction.channel.id in self.sessions:
            await interaction.response.send_message("❌ A debate is already active in this channel.", ephemeral=True)
            return

        members = []
        # Parse mentions
        for mention in debaters.split(','):
            m = mention.strip()
            if m.startswith("<@") and m.endswith(">"):
                m = m.replace("<@", "").replace("!", "").replace(">", "")
            try:
                member = await interaction.guild.fetch_member(int(m))
                members.append(member)
            except:
                continue

        if len(members) < 2:
            await interaction.response.send_message("❌ Mention at least **two valid users**.", ephemeral=True)
            return

        # Create debate session
        self.sessions[interaction.channel.id] = {
            "users": {m.id for m in members},
            "names": {m.id: m.display_name for m in members},
            "topic": topic,
            "log": []
        }

        await interaction.response.send_message(
            f"🧠 **Debate started between:** " +
            ", ".join([f"**{m.display_name}**" for m in members]) +
            f"\n📌 **Topic:** {topic}\nUse `/stop` to end the debate and get the analysis."
        )

    # ------------ STOP COMMAND ------------
    @app_commands.command(name="stop", description="Stop and analyze the ongoing debate.")
    async def stop(self, interaction: discord.Interaction):

        channel_id = interaction.channel.id
        if channel_id not in self.sessions:
            await interaction.response.send_message("❌ No ongoing debate in this channel.", ephemeral=True)
            return

        session = self.sessions.pop(channel_id)
        log = session["log"]

        if not log:
            await interaction.response.send_message("⚠️ No messages were recorded.", ephemeral=False)
            return

        topic = session["topic"]
        debate_text = "\n".join(log)

        await interaction.response.send_message("🧠 Analyzing the debate... Please wait.")

        participants = list(session["names"].values())

        prompt = f"""
You are a fair, strict, and unbiased AI debate judge.
Analyze the debate between: {', '.join(participants)}

📌 Topic: {topic}

Return the result **in EXACTLY this format**:

- Score for <DebaterName>: <score>/100
- Winner: <best debater>
- Reason:

Debate Transcript:
{debate_text}
"""

        try:
            response = openai.ChatCompletion.create(
                model="deepseek/deepseek-r1",
                messages=[{"role": "user", "content": prompt}]
            )

            result = response["choices"][0]["message"]["content"]
            await interaction.followup.send(f"🧾 **Final Judgment:**\n{result}")

        except Exception as e:
            await interaction.followup.send(f"❌ Error while analyzing:\n```{e}```")

    # ------------ MESSAGE LOGGING ------------
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
