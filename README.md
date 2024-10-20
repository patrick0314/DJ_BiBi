# DJ_BiBi

這是一個簡單的 discord 機器人，包含：音樂、遊戲等等小功能

## Pre-requisite

1. 下載 python & 對應套件 [requiements](https://github.com/patrick0314/DJ_BiBi/blob/main/requirements.txt)
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

2. 下載 [ffmpeg](https://ffmpeg.org/download.html#build-windows) ，並加入環境變數中，可參考 [youtube](https://youtu.be/hHfzHVuRx7k?t=150)

## Usage

1. git clone repository 後，新增一個資料夾 `env`，並在此資料夾內新增 `password.env`，填入你的 discord bot token
```
discord_token=<YOUR_DISCORD_TOKEN>
```

2. 新增 `tmp` 資料夾供後續機器人使用

> 可以自行在程式內增加防呆機制

3. 執行 `python main.py`

## Function

1. 主要 (Main)

* 此機器人的前綴 (prefix) 為 `;`

```
-load <cog>     : load the <cog> extension
-unload <cog>   : un-load the <cog> extension
-reload <cog>   : re-load the <cog> extension
-help           : help message
```

2. 音樂 (Music)

* 可播放 YT 歌曲，包含基本功能：播放、暫停、循環、隨機播放

* 可存取 YT 歌單並隨著 YT 歌單更新

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

3. 遊戲 (Game)

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

4. 其他 (Others)

```
-card <name> [title] [descirption] [url] : send the embedded card to <name> with [title] [description] [image url]

<> = required information, [] = optional information
```
