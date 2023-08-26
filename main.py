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

@bot.listen()
async def on_ready():
    print(f"Logged in succesfully")


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



