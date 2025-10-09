# 🎵 DJ BiBi: A Comprehensive Discord Music Bot

A feature-rich Discord music bot built with discord.py and powered by the high-performance audio engine, Lavalink. DJ BiBi supports playing music from YouTube Music, manages queues, and offers various playback controls with strict permission checks.

## ✨ Features at a Glance

Seamless Playback: Utilizes Lavalink for stable, high-quality audio streaming.

Intuitive Control: Full suite of commands including !play, !skip, !pause, !resume.

Queue Management: Advanced controls like !queue, !remove, !clear, and !shuffle.

Looping Modes: Supports Track Loop, Queue Loop, and Off modes.

Secure Permissions: Command checks ensure control commands are only usable by members in the bot's current voice channel.

Aesthetic Embeds: Uses themed embed messages for clear success and error reporting.

## 🛠️ Environment Setup & Requirements

To run DJ BiBi, you need to set up the Python environment and the external Lavalink server.

### 1. **External Requirements (Lavalink)**

The bot requires an external Lavalink server instance to handle audio processing.

- **Java Runtime Environment (JRE):** You must have **Java 17 or newer** installed. (Older versions like Java 8/11 will cause errors).

- **Lavalink Server:**

    - Download the latest `Lavalink.jar` from the [Lavalink GitHub Releases page](https://github.com/lavalink-devs/Lavalink/releases).

    - Create an `application.yml` file in the same directory as the ``.jar` to configure the password (e.g., `youshallnotpass`).

    - Run the server: `java -jar Lavalink.jar`

### 2. **Python Libraries & Configuration**

- Install Dependencies:

```Bash
pip install discord.py wavelink
```

- Configuration:

    - Create a file named config.py in the project root.

    - Fill in your Discord Bot Token and the Lavalink details (Host, Port, Password).

```Python
# config.py
DISCORD_TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"
LAVALINK_HOST = "127.0.0.1"
LAVALINK_PORT = 2333
LAVALINK_PASSWORD = "youshallnotpass"
Security Note: Remember to add config.py to your .gitignore file to prevent sharing sensitive tokens.
```

> Security Note: Remember to add config.py to your .gitignore file to prevent sharing sensitive tokens.

## 🚀 Usage and Commands

The default command prefix is `!`.

### General & Playback

| Command | Alias | Description | Permission Requirement |
|:-------:|:-----:|:-----------:|:----------------------:|
| `!join` | `!j`, `!connect` | Makes the bot join your voice channel. | User must be in a VC. |
| `!play <query/url>` | `!p` | Searches YouTube Music/URL and starts playing or queues the track. | User must be in a VC. |
| `!skip` | `!s`, `!next` | Skips the currently playing track.| Must be in bot's VC. |
| `!pause` | | Pauses playback. | Must be in bot's VC. |
| `!resume` | `!res` | `Resumes paused playback. | Must be in bot's VC. |

### Queue & Management

| Command | Alias | Description | Permission Requirement |
|:-------:|:-----:|:-----------:|:----------------------:|
| `!queue` | `!q`, `!list` | Displays the current queue and the song playing. | Must be in bot's VC. |
| `!remove <index>` | `rm`, `del` | Removes a track by its position number in the queue. | Must be in bot's VC. |
| `!clear` | `cls` | Clears all tracks from the queue (keeps the current song). | Must be in bot's VC. |
| `!shuffle` | | Randomly shuffles the order of all tracks in the queue. | Must be in bot's VC. |
| `!loop <mode>` | `repeat` | Sets loop mode: `track`, `queue`, or `off`. | Must be in bot's VC. |
| `!volume <0-1000>` | `vol` | Sets the playback volume or displays the current volume. | Must be in bot's VC. |
| `!leave` | `l`, `disconnect` | Disconnects the bot and clears the queue. | Must be in bot's VC. |

## ▶️ Running the Bot

1. Ensure the Lavalink server (Step 1) is running in a terminal window.

2. Open a second terminal window in the project root (/DJ_BiBi).

3. Run the main Python script:

```Bash
python main.py
```

> Developer Note: The project uses cogs/extensions for modularity. All music logic resides in cogs/music.py, and utility functions for embeds are in utils/embed.py.

## ⚖️ License and Disclaimer

### Copyright & Ownership

This Discord Bot project, DJ BiBi, including all source code within the cogs/, utils/, and main.py files, is developed and maintained by Patrick.Huang

### Third-Party Components Disclaimer

This project relies on external, third-party libraries and services, which operate under their own terms and conditions:

- Discord.py: Used for interacting with the Discord API.

- Wavelink: Used as the client to connect to the Lavalink server.

- Lavalink: An external, open-source audio processing server that handles media streaming.

- YouTube Music/Spotify (Indirectly): All music playback is performed through the Lavalink server and typically sourced via YouTube Music or YouTube.

**Disclaimer:** This bot is intended for personal and non-commercial use on private Discord servers. The developer of DJ BiBi is not responsible for any misuse that violates the Terms of Service of Discord, Spotify, YouTube, or any applicable copyright laws. Users are solely responsible for ensuring their usage complies with all relevant legal restrictions.