import discord
from discord.ext import commands
import queue
from yt_dlp import YoutubeDL
import time

class music_cog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.voice_client = None
        self.is_playing = False
        self.music_q = queue.Queue()
        self.curr = ""

        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}


    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info(f"ytsearch:{item}", download=False)['entries'][0]
            except Exception: 
                return False

        return {'link': info['url'], 'title': info['title']}
    

    async def check_bot_status(self, ctx):
        if ctx.author.voice and ctx.author.voice.channel:
            if not self.voice_client:
                #add another check that checks if curr voice channel = bot voice channel
                self.voice_client = await ctx.author.voice.channel.connect()
            return True
        return False
    
    async def play_after(self, ctx):
        await self.play_q(ctx)

    @commands.command(name="play", help="Plays music that you search for on Youtube")
    async def play(self, ctx, *args):
        title = " ".join(args)
        res = self.search_yt(title)
        #res = False if unable to find song
        if not res:
            await ctx.send("Unable to find song.")
            return
        
        status = await self.check_bot_status(ctx)      
        if status:
            url, title = res['link'], res['title']            
            #stop current music before executing play()
            if self.is_playing:
                print("Hello")
                self.voice_client.stop()
                #have to add delay because stop() function is delayed. not async though.
                time.sleep(1)
                
            
            self.is_playing = True
            await ctx.send(f"Now playing... {title}")
            self.voice_client.play(discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS), after=lambda e: self.bot.loop.create_task(self.play_after(ctx)))

        else:
            await ctx.send(f"Connect to a voice channel!")
        
    
    @commands.command(name="add", help="Adds the song to the queue")
    async def add(self, ctx, *args):
        title = " ".join(args)
        res = self.search_yt(title)
        if res:
            self.music_q.put(res)
            print(self.music_q.queue[0])
            if not self.is_playing:
                print("22222222222222222222222")
                await self.play_q(ctx)
            print("33333333333333333333333333333")
        else:
            await ctx.send("Unable to play song.")

    async def play_q(self, ctx):
        if not self.music_q.empty():
            await self.check_bot_status(ctx)
            res = self.music_q.get()
            link = res['link']
            self.curr = res['title']
            self.is_playing = True
            self.voice_client.play(discord.FFmpegPCMAudio(link, **self.FFMPEG_OPTIONS), after=lambda e: self.bot.loop.create_task(self.play_after(ctx)))
        else:
            self.is_playing = False
        
    
    @commands.command(name="disconnect", help="Disconnects music bot from the voice channel and resets Queue")
    async def disconnect(self, ctx):
        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.disconnect()
            await ctx.send("Disconnected Bot.")
        self.music_q = queue.Queue()
        self.voice_client = None
        self.is_playing = False
        self.curr = ""


    
    @commands.command(name='next', help="Shows next song in queue")
    async def next(self, ctx):
        if self.music_q.empty():
            await ctx.send("No songs left in queue")
        else:
            await ctx.send(f"Next song is: {self.music_q.queue[0]['title']}")
    
    @commands.command(name='pause', help='Pauses current song')
    async def pause(self, ctx):
        if self.voice_client:
            if self.voice_client.is_playing():
                self.voice_client.pause()
        else:
            await ctx.send("Action was not possible")
    
    @commands.command(name='resume', help='Resumes current song')
    async def resume(self, ctx):
        if self.voice_client:
            if self.voice_client.is_paused():
                self.voice_client.resume()
                
        else:
            await ctx.send("Action was not possible")



        