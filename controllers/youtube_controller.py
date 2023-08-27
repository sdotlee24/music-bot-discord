from yt_dlp import YoutubeDL


YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}

def search_yt(item):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try: 
            info = ydl.extract_info(f"ytsearch:{item}", download=False)['entries'][0]
        except Exception: 
            return False

    return {'link': info['url'], 'title': info['title']}