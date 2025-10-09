import asyncio
import discord
import wavelink

from discord.ext import commands
from config import LAVALINK_HOST, LAVALINK_PORT, LAVALINK_PASSWORD
from utils.embed import success_embed, error_embed, info_embed

# --- A Cog for Handling All Music-Related Commands ---
class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.loop.create_task(self.connect_nodes()) # schedule the task to connect to Lavalink nodes
    
    # --- Lavalink Connection and Events
    async def connect_nodes(self):
        await self.bot.wait_until_ready()

        # Check if a node pool already exists to prevent duplicate connections
        if not wavelink.NodePool._nodes:
            try:
                node: wavelink.Node = await wavelink.NodePool.create_node(
                    bot=self.bot,
                    host=LAVALINK_HOST,
                    port=LAVALINK_PORT,
                    password=LAVALINK_PASSWORD,
                )
                print(f"Wavelink Node {node.identifier} established")
            except Exception as e:
                print(f"Wavelink connection failed: {e}")
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Lavalink Node {node.identifier} is ready")
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.abc.Playable, reason: str):
        # Handle what happens when a track finishes playing
        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)

            channel = player.channel
            await channel.send(embed=info_embed(
                description=f"Now playing next: **{next_track.title}** - **{next_track.author}**",
            ))

    # --- Music Commands ---
    @commands.command(name="join", aliases=["j", "connect"])
    async def join_command(self, ctx: commands.Context):
        if not ctx.author.voice:
            return await ctx.send(embed=error_embed(
                description="You must be in a voice channel to use this command",
            ))
        
        # Connect or move the player to the voice channel
        player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        await ctx.send(embed=success_embed(
            title="🔊 Connected",
            description=f"Joined voice channel: **{player.channel.name}**",
        ))
    
    @commands.command(name="play", aliases=["p"])
    async def play_command(self, ctx: commands.Context, *, search: str):
        # Search and plays music from YouTube Music (or other supported sources)
        if not ctx.voice_client:
            try:
                await ctx.invoke(self.join_command)
            except Exception:
                return await ctx.send(embed=error_embed(
                    description="Please use `!join` first",
                ))

        # Search for the track using YouTube Music search engine
        tracks = await wavelink.YouTubeMusicSearch.search(query=search)
        if not tracks:
            return await ctx.send(embed=error_embed(
                description=f"Could not find any tracks for `{search}`",
            ))
        
        # Get the player instance
        player: wavelink.Player = ctx.voice_client

        # Handle playback and queue logic
        if not player.is_playing() and player.queue.is_empty:
            # If player is idle and queue is empty, start playback immediately.
            if isinstance(tracks[0], wavelink.Playlist):
                playlist = tracks[0]
                # Put the playlist tracks into the queue first.
                player.queue.extend(playlist.tracks)
                
                # Start playing the first track from the queue.
                first_track = player.queue.get()
                await player.play(first_track) 
                return await ctx.send(embed=info_embed(
                    description=f"Started playing playlist **{playlist.name}**. Added {len(playlist.tracks)} tracks to the queue.",
                ))
            else:
                track = tracks[0]
                await player.play(track)
                return await ctx.send(embed=info_embed(
                    description=f"Now playing: **{track.title}** - **{track.author}**",
                ))
        else:
            # Add the track or playlist to the queue.
            if isinstance(tracks[0], wavelink.Playlist):
                playlist = tracks[0]
                player.queue.extend(playlist.tracks)
                return await ctx.send(embed=info_embed(
                    description=f"Added playlist **{playlist.name}** ({len(playlist.tracks)} tracks) to the queue.",
                ))
            else:
                track = tracks[0]
                player.queue.put(track)
                return await ctx.send(embed=info_embed(
                    description=f"Added **{track.title}** - **{track.author}** to the queue.",
                ))

    @commands.command(name="skip", aliases=["s", "next"])
    async def skip_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not player or not player.is_playing():
            return await ctx.send(embed=error_embed(
                description="Nothing is currently playing",
            ))
        
        await player.stop()
        await ctx.send(embed=success_embed(
            description="Skipped the current track",
        ))

    @commands.command(name="pause")
    async def pause_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not player:
            return await ctx.send(embed=error_embed(
                description="The bot is not connected to a voice channel.",
            ))
        
        if player.is_paused():
            return await ctx.send(embed=info_embed(
                description="Music is already paused.",
            ))

        await player.pause()
        await ctx.send(embed=success_embed(
            description="⏸️ Music paused.",
        ))

    @commands.command(name="resume", aliases=['res'])
    async def resume_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not player:
            return await ctx.send(embed=error_embed(
                description="The bot is not connected to a voice channel.",
            ))
            
        if not player.is_paused():
            return await ctx.send(embed=info_embed(
                description="Music is not paused.",
            ))

        await player.resume()
        await ctx.send(embed=success_embed(
            description="▶️ Music resumed.",
        ))

    @commands.command(name="volume", aliases=['vol'])
    async def volume_command(self, ctx: commands.Context, volume: int = None):
        player: wavelink.Player = ctx.voice_client
        if not player:
            return await ctx.send(embed=error_embed(
                description="The bot is not connected to a voice channel.",
            ))

        # Display current volume
        if volume is None:
            return await ctx.send(embed=info_embed(
                description=f"Current volume is **{player.volume}%**.",
            ))
        
        # Modify volume
        if not 0 <= volume <= 1000:
            return await ctx.send(embed=error_embed(
                description="Volume must be a number between 0 and 1000.",
            ))

        await player.set_volume(volume)
        await ctx.send(embed=success_embed(
            description=f"🔊 Volume set to **{volume}%**.",
        ))

    @commands.command(name="queue", aliases=["q", "list"])
    async def queue_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not player or (player.queue.is_empty and not player.is_playing()):
            return await ctx.send(embed=info_embed(
                description="The queue is currently empty.",
            ))

        queue_list = []
        
        # Add currently playing song
        if player.current:
            queue_list.append(f"**Now Playing:** [{player.current.title}]({player.current.uri}) by {player.current.author}")

        # Add tracks in the queue
        for index, track in enumerate(player.queue):
            if index >= 10:
                queue_list.append(f"And {len(player.queue) - index} more track(s)...")
                break
            queue_list.append(f"**{index + 1}.** [{track.title}]({track.uri}) by {track.author}")

        await ctx.send(embed=info_embed(
            title="Music Queue",
            description="\n".join(queue_list),
        ))

    @commands.command(name="leave", aliases=["l", "disconnect"])
    async def leave_command(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send(embed=error_embed(
                description="The bot is not currently in a voice channel",
            ))
        
        # Clear the queue before disconnecting
        player: wavelink.Player = ctx.voice_client
        player.queue.clear()

        # Disconnect the player
        await ctx.voice_client.disconnect()
        await ctx.send(embed=success_embed(
            description="Disconnected from the voice channel",
        ))
        
# Setup function required to load the Cog into the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))