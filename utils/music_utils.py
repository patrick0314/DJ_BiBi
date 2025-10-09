import asyncio
import discord
import wavelink

from discord import app_commands
from discord.ext import commands
from utils.embed import success_embed, error_embed, info_embed

# --- General Functions ---
def format_time(ms):
    seconds = ms // 1000
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02}:{seconds:02}"

# --- General Check Functions ---
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

# --- Feature : Loop ---
class LoopMode(app_commands.Choice):
    OFF = app_commands.Choice(name="Off", value="off")
    TRACK = app_commands.Choice(name="Track Loop", value="track")
    QUEUE = app_commands.Choice(name="Queue Loop", value="queue")

# --- Feature : Queue ---
class QueueView(discord.ui.View):
    def __init__(self, tracks: list[wavelink.abc.Playable], current_track: wavelink.abc.Playable, bot: commands.Bot):
        super().__init__(timeout=180)
        self.tracks = tracks
        self.current_track = current_track
        self.bot = bot
        self.tracks_per_page = 10
        self.current_page = 0
        self.max_pages = (len(tracks) + self.tracks_per_page - 1) // self.tracks_per_page
        self._update_buttons()

    def get_page_embed(self):
        start = self.current_page * self.tracks_per_page
        end = start + self.tracks_per_page
        page_tracks = self.tracks[start:end]

        queue_list = []
        if self.current_page == 0 and self.current_track:
            queue_list.append(f"**Now Playing:** [{self.current_track.title}]({self.current_track.uri}) by {self.current_track.author}")
            queue_list.append("--- Queue ---")
        
        for index, track in enumerate(page_tracks):
            global_index = start + index
            queue_list.append(f"**{global_index + 1}.** [{track.title}]({track.uri}) by {track.author} ({format_time(track.length)})")

        return info_embed(
            title=f"🎶 Music Queue (Page {self.current_page + 1}/{self.max_pages})",
            description="\n".join(queue_list) if queue_list else "This page is empty.",
        )

    def _update_buttons(self):
        self.children[0].disabled = (self.current_page == 0)
        self.children[1].disabled = (self.current_page == self.max_pages - 1) or (self.max_pages == 0)

    @discord.ui.button(label="⬅️ Previous", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self._update_buttons()
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)
        else:
            await interaction.response.defer() # No action needed

    @discord.ui.button(label="Next ➡️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
            self._update_buttons()
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)
        else:
            await interaction.response.defer() # No action needed

    async def on_timeout(self):
        if self.message:
            for item in self.children:
                item.disabled = True
            await self.message.edit(content="Queue view time out", view=None)

# --- Feature : Volume ---
class VolumeView(discord.ui.View):
    def __init__(self, player: wavelink.Player, bot: commands.Bot):
        super().__init__(timeout=60)
        self.player = player
        self.bot = bot
        self.add_item(self.VolumeViewMenu(player))

    class VolumeViewMenu(discord.ui.Select):
        def __init__(self, player: wavelink.Player):
            options = []
            for i in range(11):
                volume_percent = i * 10
                volume_value = i * 100
                options.append(discord.SelectOption(
                    label=f"{volume_percent}%",
                    value=str(volume_value),
                    default=(volume_value == player.volume),
                ))
            
            # Ensure the current volume (if not a multiple of 100) is in the options
            if player.volume not in [i * 100 for i in range(11)]:
                options.append(discord.SelectOption(
                    label=f"Current: {player.volume}%",
                    value=str(player.volume),
                    default=True
                ))

            super().__init__(
                placeholder=f"Current Volume: {player.volume}%",
                options=options,
                custom_id="volume_select_menu"
            )
            
        async def callback(self, interaction: discord.Interaction):
            new_volume = int(self.values[0])
            player: wavelink.Player = self.view.player
            
            await player.set_volume(new_volume)
            
            # Update the view and embed
            self.view.stop() # Stop the old view to disable it
            await interaction.response.edit_message(
                embed=success_embed(
                    description=f"🔊 Volume set to **{new_volume}%**.",
                ),
                view=None # Remove the select menu
            )
            
    async def on_timeout(self):
        # When the view times out, disable the selection
        for item in self.children:
            item.disabled = True