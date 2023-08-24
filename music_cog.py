import discord
from discord.ext import commands
import queue
from youtube_dl import YoutubeDL

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

        return {'link': info['formats'][0]['url'], 'title': info['title']}
    
    async def check_bot_status(self, ctx):
        if ctx.author.voice and ctx.author.voice.channel:
            if not self.voice_client:
                #add another check that checks if curr voice channel = bot voice channel
                self.voice_client = await ctx.author.voice.channel.connect()
            return True
        return False
    @commands.command(name="play", help="Plays music that you search for on Youtube")
    async def play(self, ctx, *args):
        title = " ".join(args)
        res = self.search_yt(title)
        #res = False if unable to find song
        if not res:
            await ctx.send("Unable to find song.")
            return
        
        self.music_q.put(res)
        status = await self.check_bot_status(ctx)      
        if status:
            url = self.music_q.get()['link']
            self.voice_client.play(discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS), after=lambda e: print("terminated"))    
        else:
            await ctx.send(f"Connect to a voice channel!")
        
    
    @commands.command(name="add", help="Adds the song to the queue")
    async def add(self, ctx, *args):
        title = " ".join(args)
        res = self.search_yt(title)
        if res:
            self.music_q.put(res)
            if not self.is_playing:
                self.play_q(ctx)
        else:
            await ctx.send("Unable to play song.")

    async def play_q(self, ctx):
        if not self.music_q.empty:
            res = self.music_q.get()
            link = res['link']
            title = res['title']
            self.voice_client.play(discord.FFmpegPCMAudio(link, **self.FFMPEG_OPTIONS), after=lambda e: self.play_q)
        else:
            self.is_playing = False
        
    
    @commands.command(name="disconnect", help="Disconnects music bot from the voice channel")
    async def disconnect(self, ctx):
        pass


#vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())