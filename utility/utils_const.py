import yt_dlp

yt_dl_options = {
    "format": "bestaudio/best",
    "no-playlist": True
}

ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn -filter:a 'volume=0.5'"
}