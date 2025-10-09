import asyncio
import discord
import random
import wavelink

from discord.ext import commands
from config import LAVALINK_HOST, LAVALINK_PORT, LAVALINK_PASSWORD
from utils.embed import success_embed, error_embed, info_embed

# --- General Check Function ---
def is_in_voice_channel():
    # Check if the command invoker is in ANY voice channel
    async def predicate(ctx: commands.Context):
        if ctx.author.voice:
            return True
        else:
            raise commands.CheckFailure("You must be in a voice channel to use this command")

    return commands.check(predicate)

def is_in_same_voice_channel():
    # Check if the command invoker is in the SAME voice channel as the bot
    async def predicate(ctx: commands.Context):
        if not ctx.voice_client:
            return True
        if ctx.author.voice and ctx.author.voice.channel == ctx.voice_client.channel:
            return True
        else:
            raise commands.CheckFailure("You must be in the same voice channel as the bot to control playback")
    
    return commands.check(predicate)

# --- A Cog for Handling All Music-Related Commands ---
class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.loop_states = {} # 0: Off, 1: Track loop, 2: Queue loop
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
        guild_id = player.guild.id
        loop_mode = self.loop_states.get(guild_id, 0)

        if loop_mode == 1: # track loop
            await player.play(track=track)
            return
        elif loop_mode == 2: # queue loop
            player.queue.put(track)
        
        # Normal playback or queue loop -> get the next song
        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)

            channel = player.channel
            await channel.send(embed=info_embed(
                description=f"Now playing next: **{next_track.title}** - **{next_track.author}**"
            ))

    # --- Music Commands ---
    @commands.command(name="join", aliases=["j", "connect"])
    @is_in_voice_channel()
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
    @is_in_same_voice_channel()
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
    @is_in_same_voice_channel()
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

    @commands.command(name="remove", aliases=['rm', 'del'])
    @is_in_same_voice_channel()
    async def remove_command(self, ctx: commands.Context, index: int):
        player: wavelink.Player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(embed=info_embed(
                description="The queue is currently empty.",
            ))

        # Queue indexing starts from 0 internally, but users see 1-based index.
        queue_index = index - 1
        try:
            # Check if the index is valid
            if not 0 <= queue_index < len(player.queue):
                return await ctx.send(embed=error_embed(
                    description=f"Invalid queue number. Please provide a number between 1 and {len(player.queue)}.",
                ))
                
            # Remove the track
            removed_track = player.queue.pop(queue_index)
            await ctx.send(embed=success_embed(
                description=f"🗑️ Removed **{removed_track.title}** - **{removed_track.author}** from the queue.",
            ))
        except IndexError:
            await ctx.send(embed=error_embed(
                description=f"Invalid queue number. Please provide a number between 1 and {len(player.queue)}.",
            ))
        except Exception as e:
            await ctx.send(embed=error_embed(
                description=f"An unknown error occurred while removing the track: {e}",
            ))

    @commands.command(name="clear", aliases=['cls'])
    @is_in_same_voice_channel()
    async def clear_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(embed=info_embed(
                description="The queue is already empty.",
            ))

        # Check if the player is currently playing anything
        if not player.is_playing():
            # If nothing is playing, just clear the queue
            player.queue.clear()
            return await ctx.send(embed=success_embed(
                description="🗑️ Queue has been cleared.",
            ))

        # If a song is playing, we clear the queue but keep the current song playing
        queue_length = len(player.queue)
        player.queue.clear()
        await ctx.send(embed=success_embed(
            description=f"🗑️ Cleared **{queue_length}** track(s) from the queue. The current song keeps playing.",
        ))

    @commands.command(name="pause")
    @is_in_same_voice_channel()
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
    @is_in_same_voice_channel()
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

    @commands.command(name="queue", aliases=["q", "list"])
    @is_in_same_voice_channel()
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

    @commands.command(name="loop", aliases=['repeat'])
    @is_in_same_voice_channel()
    async def loop_command(self, ctx: commands.Context, mode: str = None):
        guild_id = ctx.guild.id
        current_mode = self.loop_states.get(guild_id, 0)
        modes = {
            'off': 0,
            'track': 1,
            'queue': 2,
        }
        mode_names = {
            0: 'Off',
            1: 'Track Loop (Current Song)',
            2: 'Queue Loop (Playlist)',
        }
        
        # Display current mode
        if mode is None:
            return await ctx.send(embed=info_embed(
                title="🔄 Loop Status",
                description=f"Current loop mode: **{mode_names[current_mode]}**.\n"
                            f"Usage: `!loop <track|queue|off>`",
            ))

        # Modify mode
        mode = mode.lower()
        if mode not in modes:
            return await ctx.send(embed=error_embed(
                description=f"Invalid loop mode. Use: `track`, `queue`, or `off`.",
            ))

        new_mode = modes[mode]
        self.loop_states[guild_id] = new_mode
        await ctx.send(embed=success_embed(
            description=f"Loop mode set to: **{mode_names[new_mode]}**.",
        ))

    @commands.command(name="shuffle")
    @is_in_same_voice_channel()
    async def shuffle_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not player or player.queue.is_empty:
            return await ctx.send(embed=info_embed(
                description="The queue is empty. Nothing to shuffle.",
            ))

        # Shuffle the list in place
        queue_list = list(player.queue)
        random.shuffle(queue_list)
        
        # Replace the old queue with the shuffled list
        player.queue.clear()
        player.queue.extend(queue_list)
        await ctx.send(embed=success_embed(
            description=f"🔀 Shuffled **{len(queue_list)}** tracks in the queue!",
        ))

    @commands.command(name="volume", aliases=['vol'])
    @is_in_same_voice_channel()
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

    @commands.command(name="leave", aliases=["l", "disconnect"])
    @is_in_same_voice_channel()
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

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(embed=error_embed(
                description=str(error),
            ))
        else:
            raise error

# Setup function required to load the Cog into the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))