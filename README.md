# DJ_BiBi

This project, DJ_BiBi, is a custom Discord bot that enhances servers with music and interactive games.

It allows users to play music directly from YouTube, manage playlists, and control playback with commands. Additionally, it offers multiplayer games like 1A2B, Gomoku, and Codenames, providing both entertainment and music streaming features in one bot.

Ideal for social gaming or collaborative playlists, DJ_BiBi adds fun and functionality to any Discord community.

## Pre-requisite

1. Download Python & install the required packages [requiements](https://github.com/patrick0314/DJ_BiBi/blob/main/requirements.txt)
```
discord.py     2.4.0
numpy          2.1.2
opencv_python  4.10.0.84
Pillow         9.5.0
Pillow         11.0.0
python-dotenv  1.0.1
pytube         15.0.0
yt_dlp         2024.10.7
```

2. Download [FFmpeg](https://ffmpeg.org/download.html#build-windows) and add it to your system's PATH. You can refer to [YouTube tutorials](https://youtu.be/hHfzHVuRx7k?t=150) for guidance

## Usage

1. After cloning the repository, create a folder named `env` and add a file called `password.env` inside it. In this file, enter your Discord bot token
```
discord_token=<YOUR_DISCORD_TOKEN>
```

2. Create a `tmp folder` for the bot's future use

> You can add your own fail-safe mechanisms to the program

3. Execute `python main.py`

## Function

1. Main

* The prefix for this bot is `;`

```
-load <cog>     : load the <cog> extension
-unload <cog>   : un-load the <cog> extension
-reload <cog>   : re-load the <cog> extension
-help           : help message
```

2. Music

* This bot can play YouTube songs with basic functionalities, including play, pause, loop, and shuffle

* This bot can access YouTube playlists and update in accordance with changes to the playlists

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

-lists                   : list and update all saved playlist
-(s)ave <name> <url>     : save the YT playlist as <name>
-unsave <name>           : delete the <name> playlist
-(l)ist <name>           : load the pre-saved <name> playlist
-update <name>           : update the <name>-playlist which is from YT playlist

<> = required information, [] = optional information
```

3. Game

* [1A2B (AB Game)](https://zh.wikipedia.org/zh-tw/1A2B)

* [五子棋 (Gomoku)](https://zh.wikipedia.org/zh-tw/%E4%BA%94%E5%AD%90%E6%A3%8B)

* [機密代號 (Codenames)](https://en.wikipedia.org/wiki/Codenames_(board_game))

```
AB Game:
-abstart           : start the AB game
-(g)uess <number>  : guess the 4-digit number

Gomoku:
-gostart           : start the Gomoku
-place <x> <y>     : place at (x, y)

Codenames:
-codestart         : start the Codenames
-host              : host use this command to get the answer
-code <code>       : guess <code> be author's team code

<> = required information, [] = optional information
```

4. Others

```
-card <name> [title] [descirption] [url] : send the embedded card to <name> with [title] [description] [image url]

<> = required information, [] = optional information
```
