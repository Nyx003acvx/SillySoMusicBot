import discord
from discord.ext import commands
import asyncio
import config
import logging
import os
# os.system("pip install ")
TOKEN = os.environ.get('DISCORD_TOKEN')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord')

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        intents.guilds = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            description='A high-quality music bot for Discord'
        )
        self.initial_extensions = ['cogs.music']
        self.tree.on_error = self.on_command_error

    async def setup_hook(self):
        try:
            for ext in self.initial_extensions:
                await self.load_extension(ext)
                logger.info(f'Successfully loaded extension: {ext}')
        except Exception as e:
            logger.error(f'Failed to load extension: {str(e)}')
            raise

    async def on_ready(self):
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info('------')
        logger.info(f'Discord API version: {discord.__version__}')
        logger.info(f'Number of guilds: {len(self.guilds)}')
        logger.info('Bot is ready!')

async def main():
    try:
        if not config.TOKEN:
            raise ValueError("Discord token not found in environment variables")

        bot = MusicBot()
        async with bot:
            await bot.start(config.TOKEN)
    except Exception as e:
        logger.error(f'Failed to start bot: {str(e)}')
        raise

if __name__ == '__main__':
    asyncio.run(main())