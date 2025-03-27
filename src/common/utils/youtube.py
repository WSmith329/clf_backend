import re

WATCH_URL_PATTERN = r'youtube\.com/watch\?v=([\w-]{11})'

SHORT_URL_PATTERN = r'youtu\.be/([\w-]{11})'

NOCOOKIE_EMBED_PATTERN = r'youtube(?:-nocookie)?\.com\/embed\/([\w-]{11})(?:\?.*)?'


def convert_to_embed(url: str, controls: int = 0) -> str:
    if not url:
        return url

    if re.search(NOCOOKIE_EMBED_PATTERN, url):
        return url

    watch_match = re.search(WATCH_URL_PATTERN, url)
    short_match = re.search(SHORT_URL_PATTERN, url)

    video_id = watch_match.group(1) if watch_match else (short_match.group(1) if short_match else None)

    if not video_id:
        raise ValueError(f'Invalid YouTube url: {url}')

    return f'https://www.youtube-nocookie.com/embed/{video_id}?controls={controls}'
