# Music

A simple Discord bot for streaming YouTube music directly in your server.

## Commands

```plain
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

## Features

1. **Play Music**
    - Join a Discord voice channel
    - Stream music from YouTube using direct YT URLs

2. **Basic Control**
    - commands for repeat, pause, resume, skip and stop

3. **Queue Management**
    - Display the current music queue
    - Manage the queue with shuffle, skip, and clear commands

4. **Playlist Management**
    - Save YouTube playlists
    - Play a saved playlist with a single command
    - Update saved playlists to match the corresponding YouTube playlist
