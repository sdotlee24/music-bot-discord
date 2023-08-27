import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from music_cog import music_cog

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in succesfully")


@bot.event
async def on_voice_state_update(member, before, after):
    music_cog_instance = bot.cogs.get("music_cog")

    if member == bot.user and before.channel and not after.channel:
        if music_cog_instance:
            sp_controller = music_cog_instance.sp_control
            sp_controller.generate_recommended()
            

            

@bot.listen()
async def on_message(message):
    if message.author == bot.user or message.content[0] == '!':
        return
    await message.channel.send(f"Your message was: '{message.content}'")

async def setup():
    await bot.add_cog(music_cog(bot))
    print("done")

#loading cog
asyncio.run(setup())



bot.run(os.getenv("TOKEN"))



