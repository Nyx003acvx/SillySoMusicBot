import discord
import yt_dlp
import asyncio
from config import YTDL_OPTIONS, FFMPEG_OPTIONS
import logging

logger = logging.getLogger('ytdl')

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()

        try:
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ytdl:
                logger.info(f'Extracting info from URL: {url}')
                try:
                    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                except Exception as e:
                    logger.error(f'Failed to extract info from URL: {str(e)}')
                    raise Exception(f"Could not extract info from URL: {str(e)}")

                if 'entries' in data:
                    # Take first item from a playlist
                    data = data['entries'][0]

                logger.info(f'Successfully extracted info for: {data.get("title")}')
                filename = data['url']

                try:
                    audio_source = discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS)
                    logger.info('Successfully created FFmpeg audio source')
                    return cls(audio_source, data=data)
                except Exception as e:
                    logger.error(f'Failed to create FFmpeg audio source: {str(e)}')
                    raise Exception(f"Error creating audio source: {str(e)}")

        except Exception as e:
            logger.error(f'Error in from_url: {str(e)}')
            raise