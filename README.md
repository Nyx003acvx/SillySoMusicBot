1. Create your app on [Discord Developer Portal](https://discord.com/developers/applications)
     - setup,
     - allow intents

 git clone (https://github.com/Nyx003acvx/SillySoMusicBot)
   cd discord-music-bot
   ```

2. **Install Python Dependencies**
   ```bash
   # Using pip
   pip install discord.py yt-dlp PyNaCl

   # Using poetry
   poetry add discord.py yt-dlp PyNaCl
   ```

3. **Install FFmpeg**
   - On Ubuntu/Debian:
     ```bash
     sudo apt update
     sudo apt install ffmpeg
     ```
   - On Windows:
     - Download FFmpeg from the [official website](https://ffmpeg.org/download.html)
     - Add FFmpeg to your system PATH
   - On macOS:
     ```bash
     brew install ffmpeg
     ```

4. **Set up Discord Bot**
   1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
   2. Create a new application
   3. Go to the Bot section and create a bot
   4. Enable these Privileged Gateway Intents:
      - PRESENCE INTENT
      - SERVER MEMBERS INTENT
      - MESSAGE CONTENT INTENT
   5. Copy the bot token
   6. Set the token as an environment variable:
      ```bash
      # On Linux/Mac
      export DISCORD_TOKEN='your_bot_token_here'

      # On Windows
      set DISCORD_TOKEN=your_bot_token_here
      ```

5. **Run the Bot**
   ```bash
   python bot.py
   ```

## Usage

The bot uses Discord's slash commands. Type `/` in your Discord server to see the available commands:

- `/join` - Bot joins your voice channel
- `/play [query]` - Play music from YouTube (URL or search term)
- `/search [query]` - Search for songs with interactive selection
- `/pause` - Pause the current song
- `/resume` - Resume playback
- `/stop` - Stop playback and clear the queue
- `/queue` - Show the current queue
- `/leave` - Bot leaves the voice channel

## Troubleshooting

1. **No audio playback**
   - Verify FFmpeg is installed correctly:
     ```bash
     ffmpeg -version
