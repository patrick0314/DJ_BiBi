import asyncio
import discord
import random
import wavelink

from discord import app_commands
from discord.ext import commands
from config import LAVALINK_HOST, LAVALINK_PORT, LAVALINK_PASSWORD
from utils.embed import success_embed, error_embed, info_embed
from utils.music_utils import format_time, is_in_voice_channel, is_in_same_voice_channel, LoopMode, QueueView, VolumeView

# --- A Cog for Handling All Music-Related Commands ---
class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.loop_states = {} # 0: Off, 1: Track loop, 2: Queue loop
        self.auto_leave_timers = {} # tracks the auto-leave task for each guild
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

    async def start_auto_leave_timer(self, player: wavelink.Player, delay: int = 300):
        guild_id = player.guild.id
        channel = player.channel
        if guild_id in self.auto_leave_timers and not self.auto_leave_timers[guild_id].done():
            self.auto_leave_timers[guild_id].cancel()
        
        async def disconnect_task():
            try:
                await asyncio.sleep(delay=delay)
                if player.is_playing() or not player.queue.is_empty:
                    return
                
                await player.disconnect()
                await channel.send(embed=info_embed(
                    description=f"Inactivity. Disconnected from **{channel.name}**"
                ))
                del self.auto_leave_timers[guild_id]
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Auto-leave task error: {e}")
        
        # Start the new task
        task = self.bot.loop.create_task(disconnect_task())
        self.auto_leave_timers[guild_id] = task

    def stop_auto_leave_timer(self, guild_id: int):
        if guild_id in self.auto_leave_timers and not self.auto_leave_timers[guild_id].done():
            self.auto_leave_timers[guild_id].cancel()
            del self.auto_leave_timers[guild_id]

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

            self.stop_auto_leave_timer(guild_id=guild_id) # new song is playing, ensure timer is stopped
        else:
            await self.start_auto_leave_timer(player=player, delay=300) # queue is empty, start the auto-leave timer

    # --- Music Commands ---
    @app_commands.command(name="join", description="Makes the bot join your voice channel.")
    @is_in_voice_channel()
    async def join_command(self, interaction: discord.Interaction):
        channel = interaction.user.voice.channel
        player: wavelink.Player = interaction.guild.voice_client
        if player and player.channel == channel:
            return await interaction.response.send_message(
                embed=info_embed(description=f"I am already connected to **{channel.name}**."),
                ephemeral=True
            )

        # Connect or move the player to the voice channel
        player = await channel.connect(cls=wavelink.Player)
        await interaction.response.send_message(
            embed=success_embed(
                title="🔊 Connected",
                description=f"Joined voice channel: **{player.channel.name}**"
            )
        )
    
    @app_commands.command(name="play", description="Searches for a track/playlist (YouTube Music link or keywords) and starts playback.")
    @app_commands.describe(search="The song title, artist, or YouTube Music URL.")
    @is_in_voice_channel()
    async def play_command(self, interaction: discord.Interaction, search: str):
        # Search and plays music from YouTube Music (or other supported sources)
        player: wavelink.Player = interaction.guild.voice_client
        guild_id = interaction.guild.id
        await interaction.response.defer()
        if not player:
            channel = interaction.user.voice.channel
            try:
                player = await channel.connect(cls=wavelink.Player)
                join_msg = f"🔊 Joined **{channel.name}**! " 
            except Exception:
                return await interaction.followup.send(
                    embed=error_embed(
                        description="Could not automatically join your voice channel. Check bot permissions."
                    ), ephemeral=True
                )
        else:
            join_msg = "" 

        # Search for the track using YouTube Music search engine
        # Delay for searching
        try:
            tracks = await wavelink.YouTubeMusicSearch.search(query=search)
        except Exception as e:
            print(f"Wavelink Search Error: {e}")
            tracks = None
            
        if not tracks:
            return await interaction.followup.send(
                embed=error_embed(description=f"Could not find any tracks for `{search}`"),
                ephemeral=True
            )

        self.stop_auto_leave_timer(guild_id=guild_id)
        if not player.is_playing() and player.queue.is_empty:
            # Start playing if idle
            if isinstance(tracks[0], wavelink.Playlist):
                playlist = tracks[0]
                player.queue.extend(playlist.tracks)
                first_track = player.queue.get()
                await player.play(first_track)
                return await interaction.followup.send(embed=info_embed(
                    description=f"{join_msg} Started playing playlist **{playlist.name}**. Added {len(playlist.tracks)} tracks to the queue.",
                ))
            else:
                track = tracks[0]
                await player.play(track)
            return await interaction.followup.send(embed=info_embed(
                description=f"{join_msg} Now playing: **{track.title}** - **{track.author}**",
            ))
        else:
            # Add to queue
            if isinstance(tracks[0], wavelink.Playlist):
                playlist = tracks[0]
                player.queue.extend(playlist.tracks)
                return await interaction.followup.send(embed=info_embed(
                    description=f"Added playlist **{playlist.name}** ({len(playlist.tracks)} tracks) to the queue.",
                ))
            else:
                track = tracks[0]
                player.queue.put(track)
                return await interaction.followup.send(embed=info_embed(
                    description=f"Added **{track.title}** - **{track.author}** to the queue.",
                ))

    @app_commands.command(name="skip", description="Skips the currently playing track.")
    @is_in_same_voice_channel()
    async def skip_command(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client 
        if not player or not player.is_playing():
            return await interaction.response.send_message(
                embed=error_embed(description="Nothing is currently playing"),
                ephemeral=True, # private response
            )
        
        await player.stop()
        await interaction.response.send_message(
            embed=success_embed(description="Skipped the current track")
        )

    @app_commands.command(name="remove", description="Removes a track from the queue by its queue number (1st, 2nd, etc.).")
    @app_commands.describe(index="The queue position of the track to remove (e.g., 1).")
    @is_in_same_voice_channel()
    async def remove_command(self, interaction: discord.Interaction, index: app_commands.Range[int, 1]): 
        player: wavelink.Player = interaction.guild.voice_client
        if not player or player.queue.is_empty:
            return await interaction.response.send_message(
                embed=info_embed(description="The queue is currently empty."),
                ephemeral=True
            )

        # Queue indexing starts from 0 internally, but users see 1-based index.
        queue_index = index - 1 
        if not 0 <= queue_index < len(player.queue): # Check if the index is valid
            return await interaction.response.send_message(
                embed=error_embed(description=f"Invalid queue number. Please provide a number between 1 and {len(player.queue)}."),
                ephemeral=True
            )
        try:
            # Remove the track
            removed_track = player.queue.pop(queue_index)
            await interaction.response.send_message(
                embed=success_embed(description=f"🗑️ Removed **{removed_track.title}** - **{removed_track.author}** from the queue."),
            )
        except Exception as e:
            await interaction.response.send_message(
                embed=error_embed(description=f"An unknown error occurred while removing the track: {e}"),
                ephemeral=True
            )

    @app_commands.command(name="clear", description="Clears all tracks from the music queue.")
    @is_in_same_voice_channel()
    async def clear_command(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player or player.queue.is_empty:
            return await interaction.response.send_message(
                embed=info_embed(description="The queue is already empty."),
                ephemeral=True
            )

        # Check if the player is currently playing anything
        if not player.is_playing():
            # If nothing is playing, just clear the queue
            player.queue.clear()
            return await interaction.response.send_message(
                embed=success_embed(description="🗑️ Queue has been cleared."),
            )

        # If a song is playing, we clear the queue but keep the current song playing
        queue_length = len(player.queue)
        player.queue.clear()
        await interaction.response.send_message(
            embed=success_embed(description=f"🗑️ Cleared **{queue_length}** track(s) from the queue. The current song keeps playing."),
        )

    @app_commands.command(name="pause", description="Pauses the currently playing track.")
    @is_in_same_voice_channel()
    async def pause_command(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            return await interaction.response.send_message(
                embed=error_embed(description="The bot is not connected to a voice channel."),
                ephemeral=True # private response
            )
        
        if player.is_paused():
            return await interaction.response.send_message(
                embed=info_embed(description="Music is already paused."),
                ephemeral=True # private response
            )

        await player.pause()
        await interaction.response.send_message(
            embed=success_embed(description="⏸️ Music paused.")
        )

    @app_commands.command(name="resume", description="Resumes paused playback.")
    @is_in_same_voice_channel()
    async def resume_command(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            return await interaction.response.send_message(
                embed=error_embed(description="The bot is not connected to a voice channel."),
                ephemeral=True # private response
            )
            
        if not player.is_paused():
            return await interaction.response.send_message(
                embed=info_embed(description="Music is not paused."),
                ephemeral=True # private response
            )

        await player.resume()
        await interaction.response.send_message(
            embed=success_embed(description="▶️ Music resumed.")
        )

    @app_commands.command(name="nowplaying", description="Displays detailed information about the currently playing track.")
    @is_in_same_voice_channel()
    async def nowplaying_command(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player or not player.is_playing():
            return await interaction.response.send_message(
                embed=info_embed(description="Nothing is currently playing."),
                ephemeral=True
            )

        # Calculate time (in milliseconds)
        track = player.current
        position_ms = player.position
        total_length_ms = track.length

        # Build progress bar
        bar_length = 25
        progress = int((position_ms / total_length_ms) * bar_length)
        # Use an empty space to prevent the progress bar from being too condensed
        progress_bar = f"[`{'█' * progress}{'░' * (bar_length - progress)}`]" 

        # Build the final description
        description = (
            f"**{track.title}**\n"
            f"by {track.author}\n\n"
            f"{format_time(position_ms)} {progress_bar} {format_time(total_length_ms)}"
        )
        
        embed = discord.Embed(
            title="🎶 Now Playing",
            description=description,
            color=0x4E93FF # A distinct blue color for NP
        )
        
        # Set the thumbnail using the track's album art URL (if available)
        if track.thumbnail:
            embed.set_thumbnail(url=track.thumbnail)
        
        # Add the loop status and a link to the song
        embed.add_field(name="Source", value=f"[Click Here]({track.uri})", inline=True)
        loop_mode = self.loop_states.get(interaction.guild.id, 0)
        mode_names = { 0: 'Off', 1: 'Track Loop', 2: 'Queue Loop', }
        embed.add_field(name="Loop", value=mode_names[loop_mode], inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="queue", description="Displays the music queue with interactive paging buttons.")
    @is_in_same_voice_channel()
    async def queue_command(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player or (player.queue.is_empty and not player.is_playing()):
            return await interaction.response.send_message(
                embed=info_embed(description="The queue is currently empty."),
                ephemeral=True
            )

        # Display queue view
        queue_tracks_for_view = list(player.queue)
        view = QueueView(
            tracks=queue_tracks_for_view, 
            current_track=player.current, 
            bot=self.bot
        )

        # Save message for on_timeout
        response_message = await interaction.response.send_message(
            embed=view.get_page_embed(), 
            view=view
        )
        view.message = response_message

    @app_commands.command(name="loop", description="Sets the playback loop mode.")
    @app_commands.describe(mode="Choose the loop mode.")
    @is_in_same_voice_channel()
    async def loop_command(self, interaction: discord.Interaction, mode: LoopMode):
        guild_id = interaction.guild.id
        mode_value = mode.value
        modes = { 'off': 0, 'track': 1, 'queue': 2, }
        mode_names = { 0: 'Off', 1: 'Track Loop (Current Song)', 2: 'Queue Loop (Playlist)', }

        # Modify mode
        new_mode = modes[mode_value]
        self.loop_states[guild_id] = new_mode
        await interaction.response.send_message(
            embed=success_embed(description=f"Loop mode set to: **{mode_names[new_mode]}**."),
        )

    @app_commands.command(name="shuffle", description="Randomly shuffles the order of all tracks in the queue.")
    @is_in_same_voice_channel()
    async def shuffle_command(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player or player.queue.is_empty:
            return await interaction.response.send_message(
                embed=info_embed(description="The queue is empty. Nothing to shuffle."),
                ephemeral=True
            )

        # Shuffle the list in place
        queue_list = list(player.queue)
        random.shuffle(queue_list)
        
        # Replace the old queue with the shuffled list
        player.queue.clear()
        player.queue.extend(queue_list)
        await interaction.response.send_message(
            embed=success_embed(description=f"🔀 Shuffled **{len(queue_list)}** tracks in the queue!"),
        )

    @app_commands.command(name="volume", description="Sets the player volume or shows the interactive menu.")
    @is_in_same_voice_channel()
    async def volume_command(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client
        if not player:
            return await interaction.response.send_message(
                embed=error_embed(description="The bot is not connected to a voice channel."),
                ephemeral=True
            )

        # Command without arugments
        view = VolumeView(player=player, bot=self.bot)
        await interaction.response.send_message(
            embed=info_embed(
                title="🔊 Adjust Volume",
                description=f"Current volume is **{player.volume}%**. Please select a new volume level from the menu below."
            ),
            view=view,
            ephemeral=True
        )

    @app_commands.command(name="leave", description="Disconnects the bot and clears the queue.")
    @is_in_same_voice_channel()
    async def leave_command(self, interaction: discord.Interaction):
        player: wavelink.Player = interaction.guild.voice_client 
        if not player:
            return await interaction.response.send_message(
                embed=error_embed(description="The bot is not currently in a voice channel"),
                ephemeral=True
            )
        
        # Clear the queue before disconnecting
        player.queue.clear()

        # Disconnect the player
        await player.disconnect()
        await interaction.response.send_message(
            embed=success_embed(description="Disconnected from the voice channel")
        )

# Setup function required to load the Cog into the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))