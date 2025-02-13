import discord
from discord.ext import commands
import asyncio
from utils.ytdl import YTDLSource
from utils.helpers import format_time
import logging
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('music_cog')

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.current_songs = {}
        logger.info('Music cog initialized')

    def get_queue(self, ctx):
        return self.queues.get(ctx.guild.id, [])

    @commands.command(name='join', help='Joins a voice channel')
    async def join(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("You're not connected to a voice channel.")

        try:
            channel = ctx.author.voice.channel
            logger.info(f'Attempting to join channel: {channel.name} (ID: {channel.id})')

            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect(timeout=20.0, reconnect=True)

            logger.info(f'Bot joined voice channel: {channel.name}')
            await ctx.send(f'Joined {channel.name}! 🎵')
        except discord.ClientException as e:
            logger.error(f'Failed to connect to voice channel: {str(e)}')
            await ctx.send("I couldn't connect to the voice channel. Please try again.")
        except asyncio.TimeoutError:
            logger.error('Connection to voice channel timed out')
            await ctx.send("Connection timed out. Please try again.")
        except Exception as e:
            logger.error(f'Error joining voice channel: {str(e)}')
            await ctx.send(f'Error joining voice channel: {str(e)}')

    @commands.command(name='play', help='Plays a song from YouTube')
    async def play(self, ctx, *, url):
        if ctx.voice_client is None:
            try:
                await self.join(ctx)
            except Exception as e:
                logger.error(f'Failed to join voice channel: {str(e)}')
                return await ctx.send("I couldn't join your voice channel.")

        if not ctx.voice_client or not ctx.voice_client.is_connected():
            return await ctx.send("I'm not connected to a voice channel.")

        async with ctx.typing():
            try:
                logger.info(f'Attempting to play URL: {url}')
                player = await YTDLSource.from_url(url, loop=self.bot.loop)
                logger.info(f'Successfully created player for: {player.title}')

                if ctx.voice_client.is_playing():
                    self.queues.setdefault(ctx.guild.id, []).append(player)
                    await ctx.send(f'🎵 Added to queue: {player.title}')
                    logger.info(f'Added to queue: {player.title}')
                else:
                    def after_playing(error):
                        if error:
                            logger.error(f'Error after playing: {str(error)}')
                        asyncio.run_coroutine_threadsafe(
                            self.play_next(ctx), self.bot.loop
                        )

                    ctx.voice_client.play(player, after=after_playing)
                    self.current_songs[ctx.guild.id] = player
                    await ctx.send(f'🎵 Now playing: {player.title}')
                    logger.info(f'Now playing: {player.title}')
            except Exception as e:
                logger.error(f'Error playing song: {str(e)}')
                await ctx.send(f'An error occurred while playing the song: {str(e)}')

    async def play_next(self, ctx):
        try:
            if ctx.guild.id in self.queues and self.queues[ctx.guild.id]:
                next_player = self.queues[ctx.guild.id].pop(0)
                logger.info(f'Playing next song: {next_player.title}')

                def after_playing(error):
                    if error:
                        logger.error(f'Error after playing: {str(error)}')
                    asyncio.run_coroutine_threadsafe(
                        self.play_next(ctx), self.bot.loop
                    )

                ctx.voice_client.play(next_player, after=after_playing)
                self.current_songs[ctx.guild.id] = next_player
                await ctx.send(f'🎵 Now playing: {next_player.title}')
                logger.info(f'Started playing: {next_player.title}')
        except Exception as e:
            logger.error(f'Error in play_next: {str(e)}')

    @commands.command(name='pause', help='Pauses the current song')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send('⏸ Paused')
        else:
            await ctx.send('Nothing is playing.')

    @commands.command(name='resume', help='Resumes the current song')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send('▶ Resumed')
        else:
            await ctx.send('Nothing is paused.')

    @commands.command(name='skip', help='Skips the current song')
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send('⏭ Skipped')
        else:
            await ctx.send('Nothing is playing.')

    @commands.command(name='stop', help='Stops playing and clears the queue')
    async def stop(self, ctx):
        if ctx.voice_client:
            self.queues[ctx.guild.id] = []
            ctx.voice_client.stop()
            await ctx.send('⏹ Stopped and cleared queue')

    @commands.command(name='queue', help='Shows the current queue')
    async def queue(self, ctx):
        queue = self.get_queue(ctx)
        if not queue and ctx.guild.id not in self.current_songs:
            return await ctx.send('Queue is empty')

        embed = discord.Embed(title='Music Queue', color=discord.Color.blue())

        if ctx.guild.id in self.current_songs:
            current = self.current_songs[ctx.guild.id]
            embed.add_field(
                name='Now Playing',
                value=f'{current.title} ({format_time(current.duration)})',
                inline=False
            )

        if queue:
            queue_list = '\n'.join(
                f'{i+1}. {song.title} ({format_time(song.duration)})'
                for i, song in enumerate(queue)
            )
            embed.add_field(name='Queue', value=queue_list, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='volume', help='Changes the volume (0-100)')
    async def volume(self, ctx, volume: int):
        if ctx.voice_client is None:
            return await ctx.send('Not connected to a voice channel.')

        if 0 <= volume <= 100:
            ctx.voice_client.source.volume = volume / 100
            await ctx.send(f'🔊 Volume set to {volume}%')
        else:
            await ctx.send('Volume must be between 0 and 100')

    @commands.command(name='leave', help='Leaves the voice channel')
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.queues[ctx.guild.id] = []
            if ctx.guild.id in self.current_songs:
                del self.current_songs[ctx.guild.id]
            await ctx.send('👋 Goodbye!')
    
async def setup(bot):
    await bot.add_cog(Music(bot))