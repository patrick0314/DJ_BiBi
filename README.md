# DJ_BiBi
這是一個簡單的 discord 機器人，包含：音樂、遊戲等等小功能

## Pre-requisite

1. 下載 python & 對應套件
```
asyncio       3.4.3
discord.py    2.4.0
numpy         2.0.2
Pillow        9.5.0
pytube        15.0.0
yt_dlp        2024.8.6
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

0. prefix = `;`

1. 音樂 (Music)

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

-(s)ave <name> <url>     : save the YT playlist as <name>
-(l)ist <name>           : load the pre-saved <name> playlist
-update <name>           : update the <name>-playlist which is from YT playlist

<> = required information, [] = optional information
```

2. 遊戲 (Game)

3. 其他 (Others)
