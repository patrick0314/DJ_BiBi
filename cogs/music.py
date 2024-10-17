import os
import random
import asyncio
import discord
import datetime

from pytube import Playlist
from dotenv import dotenv_values
from utility.embed import embed_base
from discord.ext import commands, tasks
from utility.utils_const import ytdl, ffmpeg_options

class Music(commands.Cog):
    tz = datetime.timezone(datetime.timedelta(hours=8))
    everyday = datetime.time(hour=0, minute=0, tzinfo=tz)
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.playing = {}
        self.repeating = {}
        self.queues = {}
        self.voices = {}
        self.playlist = dotenv_values(dotenv_path="./env/playlist.env")

        # Start fetch
        self.updateRoutine.start()

    @commands.command(name="join", aliases=["j"])
    async def join(self, ctx):
        try:
            voice = await ctx.author.voice.channel.connect()
            self.voices[voice.guild.id] = voice

            # Initial
            self.playing[ctx.guild.id] = None
            self.repeating[ctx.guild.id] = True

            # Message
            await ctx.send(embed=embed_base(ctx, title="Cutie Bibi is coming (o･e･)♡", color="green", author=False))
        except Exception as e:
            print(e)

    async def play_next(self, ctx):
        try:
            # Repeat playing song
            if self.repeating[ctx.guild.id] and self.playing[ctx.guild.id] != None:
                self.queues[ctx.guild.id].append(self.playing[ctx.guild.id])
            # Play next song
            if self.queues[ctx.guild.id] != []:
                info = self.queues[ctx.guild.id].pop(0)
                await self.play(ctx, info[0], True)
            else:
                # Delete queue if no next song
                del self.queues[ctx.guild.id]
                del self.playing[ctx.guild.id]
        except Exception as e:
            print(e)

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, link, next=False, claim=True):
        try:
            # Check if bot in vc or not
            if ctx.guild.id not in self.voices:
                await ctx.send(embed=embed_base(ctx, title="BiBi has not joined the vc.", color="red", author=False))
                raise
            # Check if the URL include "list" or not
            if "list" in link:
                await ctx.send(embed=embed_base(ctx, title="Please not enter YT list.", color="red", author=False))
                raise

            # Load YT from URL
            self.loop = asyncio.get_event_loop()
            data = await self.loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))

            # Get YT info
            song = data["url"]
            title = data["title"]
            duration = data["duration"]
            info = (link, ctx.message.author, title, duration)

            # Play
            if ctx.guild.id not in self.queues:
                # First play
                self.queues[ctx.guild.id] = []
                self.playing[ctx.guild.id] = info
                player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
                await ctx.send(embed=embed_base(ctx, title="Now playing: ", description=f"{self.playing[ctx.guild.id][2]} - {self.playing[ctx.guild.id][1]}", color="green", author=False))
                self.voices[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
            elif next == True:
                # Next play
                self.playing[ctx.guild.id] = info
                player = discord.FFmpegOpusAudio(song, **ffmpeg_options)
                await ctx.send(embed=embed_base(ctx, title="Now playing: ", description=f"{self.playing[ctx.guild.id][2]} - {self.playing[ctx.guild.id][1]}", color="green", author=False))
                self.voices[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
            else:
                # Add song
                self.queues[ctx.guild.id].append(info)

                if claim: await ctx.send(embed=embed_base(ctx, title="Added Song", description=title, color="green"))
        except Exception as e:
            print(e)

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx, num=10):
        try:
            if ctx.guild.id not in self.playing or self.playing[ctx.guild.id] == None:
                await ctx.send(embed=embed_base(ctx, title="There is no song in queue.", color="red", author=False))
                raise
                
            # List queue
            length = len(self.queues[ctx.guild.id])
            queue_message = f"\nNow Playing: {self.playing[ctx.guild.id][2]} - {self.playing[ctx.guild.id][1]}\n\n"
            for i in range(min(length, num)):
                queue_message += f"{i+1}. {self.queues[ctx.guild.id][i][2]} - {self.queues[ctx.guild.id][i][1]}\n"

            await ctx.send(embed=embed_base(ctx, title="Queue", description=queue_message, color="orange", author=False))
        except Exception as e:
            print(e)

    @commands.command(name="repeat")
    async def repeat(self, ctx):
        try:
            if self.repeating[ctx.guild.id]:
                self.repeating[ctx.guild.id] = False

                await ctx.send(embed=embed_base(ctx, title="Repeat Disabled", color="red"))
            else:
                self.repeating[ctx.guild.id] = True

                await ctx.send(embed=embed_base(ctx, title="Repeat Enabled", color="green"))
        except Exception as e:
            print(e)
    
    @commands.command(name="shuffle")
    async def shuffle(self, ctx):
        try:
            if ctx.guild.id in self.queues:
                random.shuffle(self.queues[ctx.guild.id])
                await self.queue(ctx)
            else:
                await ctx.send(embed=embed_base(ctx, title="There is no queue to shuffle.", color="red"))
        except Exception as e:
            print(e)

    @commands.command(name="pause")
    async def pause(self, ctx):
        try:
            self.voices[ctx.guild.id].pause()

            await ctx.send(embed=embed_base(ctx, title="Pause", color="red"))
        except Exception as e:
            print(e)

    @commands.command(name="resume")
    async def resume(self, ctx):
        try:
            self.voices[ctx.guild.id].resume()

            await ctx.send(embed=embed_base(ctx, title="Resume", color="green"))
        except Exception as e:
            print(e)

    @commands.command(name="skip")
    async def skip(self, ctx, num=0):
        try:
            if num == 0:
                if not self.repeating[ctx.guild.id]: self.playing[ctx.guild.id] = None
                self.voices[ctx.guild.id].stop()
            else:
                self.queues[ctx.guild.id].pop(num - 1)

            await ctx.send(embed=embed_base(ctx, title="Skip", color="orange"))
        except Exception as e:
            print(e)

    @commands.command(name="clear")
    async def clear(self, ctx):
        self.playing[ctx.guild.id] = None
        if ctx.guild.id in self.queues:
            self.queues[ctx.guild.id].clear()

            await ctx.send(embed=embed_base(ctx, title="Clear", color="orange"))
        else:
            await ctx.send(embed=embed_base(ctx, title="There is no queue to clear", color="red"))

    @commands.command(name="stop")
    async def stop(self, ctx):
        self.playing[ctx.guild.id] = None
        try:
            if ctx.guild.id in self.queues:
                del self.queues[ctx.guild.id]
                del self.playing[ctx.guild.id]
                del self.repeating[ctx.guild.id]
            if self.voices[ctx.guild.id].is_playing(): self.voices[ctx.guild.id].stop()
            if ctx.guild.id in self.voices:
                await self.voices[ctx.guild.id].disconnect()
                del self.voices[ctx.guild.id]

                await ctx.send(embed=embed_base(ctx, title="Bibi wants to sleep (๑•́ωก̀๑)", color="green", author=False))
        except Exception as e:
            print(e)

    @commands.command(name="save", aliases=["s"])
    async def save(self, ctx, name, mode=None):
        try:
            # Set the write mode, "r": new file, "a": add below
            if mode == "clear": mode = "w"
            elif os.path.exists(f"./playlist/{name}.txt"): mode = "a"
            else: mode = "w"

            # Save
            save_message = ""
            with open(f"./playlist/{name}.txt", mode) as f:
                f.write(self.playing[ctx.guild.id][0] + "\n")
                save_message += (self.playing[ctx.guild.id][2] + "\n")
                for i in range(len(self.queues[ctx.guild.id])):
                    f.write(self.queues[ctx.guild.id][i][0] + "\n")
                    save_message += (f"{i+1}. " + self.queues[ctx.guild.id][i][2] + "\n")
            
            await ctx.send(embed=embed_base(ctx, title=f"Save the song below into {name}", description=save_message, color="green", author=False))
        except Exception as e:
            print(e)

    @commands.command(name="list", aliases=["l"])
    async def list(self, ctx, name):
        try:
            # Check file exists or not
            if not os.path.exists(f"./playlist/{name}.txt"):
                await ctx.send(embed=embed_base(ctx, title=f"BiBi do not find the playlist called {name}.", color="red", author=False))
                raise
            # Check if bot in vc or not
            if ctx.guild.id not in self.voices:
                await ctx.send(embed=embed_base(ctx, title="BiBi has not joined the vc.", color="red", author=False))
                raise
            
            # Load playlist
            await ctx.send(embed=embed_base(ctx, title=f"Start add songs in {name}.", color="green", author=False))

            f = open(f"./playlist/{name}.txt")
            for line in f.readlines():
                await self.play(ctx, line[:-1], claim=False)
                await asyncio.sleep(1)
                if ctx.guild.id not in self.voices or not self.voices[ctx.guild.id].is_playing(): raise
            f.close()
        except Exception as e:
            print(e)

    @commands.command(name="supervise")
    async def supervise(self, ctx, name, url):
        try:
            # Check set already or not YT list
            if name in self.playlist:
                await ctx.send(embed=embed_base(ctx, title="Have supervised.", color="red", author=False))
                raise
            elif "&list=" not in url:
                await ctx.send(embed=embed_base(ctx, title="Not YT list.", color="red", author=False))
                raise
            
            # Add new playlist in playlist.env
            with open("./env/playlist.env", "a") as f:
                f.write(f"{name} = {url}\n")
            f.close()
            await self.fetchList(url, name)
            self.playlist = dotenv_values(dotenv_path="./env/playlist.env")

            await ctx.send(embed=embed_base(ctx, title=f"Supervise {name} Successfully", color="green", author=False))
        except Exception as e:
            print(e)
    
    @commands.command(name="unsupervise")
    async def unsupervise(self, ctx, name):
        try:
            if name not in self.playlist:
                await ctx.send(embed=embed_base(ctx, title="No this playlist.", color="red", author=False))
                raise

            # Delete <name>-playlist
            with open("./env/playlist.env", "r") as f:
                lines = f.readlines()
            f.close()
            with open("./env/playlist.env", "w") as f:
                for line in lines:
                    if line.split(" ")[0] == name: continue
                    else: f.write(line)
            f.close()
            os.remove(f"./playlist/{name}.txt")
            self.playlist = dotenv_values(dotenv_path="./env/playlist.env")

            await ctx.send(embed=embed_base(ctx, title=f"Unsupervise {name} Successfully", color="green", author=False))
        except Exception as e:
            print(e)
    
    @commands.command(name="update")
    async def update(self, ctx, name):
        try:
            # Update <name>-playlist
            await self.fetchList(self.playlist[name], name)

            await ctx.send(embed=embed_base(ctx, title=f"Update {name} Successfully", color="green", author=False))
        except Exception as e:
            print(e)

    @tasks.loop(time=everyday)
    async def updateRoutine(self):
        try:
            # Fetch all playlist
            for key in self.playlist.keys():
                await self.fetchList(self.playlist[key], key)
        except Exception as e:
            print(e)
    
    async def fetchList(self, url, name):
        try:
            # Get all url
            songs = Playlist(url)
            songs = songs.video_urls

            # Save playlist
            output = os.path.join("./playlist", f"{name}.txt")
            with open(output, "w") as f:
                for song in songs:
                    f.write(str(song) + "\n")
            f.close()
        except Exception as e:
            print(e)
    
    @commands.command(name="music_help")
    async def music_help(self, ctx):
        try:
            help_message = """
# Music Command (`;`)
```
-(j)oin                : call bot join the vc
-(p)lay <URL>          : play the song of <URL>
-(q)ueue [num]         : list the top [num] / 10 songs on the playlist
-repeat                : switch the repeat mode
-shuffle               : shuffle the playlist
-pause                 : pause the song
-resume                : resume the song
-skip [num]            : skip the [num]-th song in the playlist, 0: playing song
-clear                 : clear all queue except for playing song
-stop                  : call bot leave the vc

-(s)ave <name>           : save the current playlist into <name> playlist
-(l)ist <name>           : load the pre-saved <name> playlist
-supervise <name> <url>  : save the YT playlist as <name>-playlist
-unsupervise <name>      : delete the <name>-playlist
-update <name>           : update the <name>-playlist which is from YT playlist

<> = required information, [] = optional information
```
            """
            await ctx.send(embed=embed_base(ctx, description=help_message, color="orange", author=False))
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Music(bot))