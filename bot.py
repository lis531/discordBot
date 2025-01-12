import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
import yt_dlp
import os

BOT_TOKEN = "MTA4MjczOTkyNDAyMjg2MTg1Ng.Gtg1cD.QIgWEVho2SGOvH_-WEyL8-qPeFPvkCUVwudvQY"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

async def download_youtube_video(link):
    for file in os.listdir("downloaded_songs"):
        try:
            os.remove(os.path.join("downloaded_songs", file))
            print(f"Removed: {file}")
        except Exception as e:
            print(f"Failed to remove {file}: {e}")
    if not link.startswith('https://www.youtube.com'):
        link = await get_first_youtube_result(link)
    
    download_dir = "downloaded_songs"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{download_dir}/%(id)s.%(ext)s',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            filename = f"{download_dir}/{info['id']}.mp3"
            return filename
    except Exception as e:
        print(f"Download error: {e}")
        return None

# !help
@bot.hybrid_command(
    name='help',
    brief='Show all commands',
    description='Show all commands available'
)
async def help_command(ctx):
    embed = discord.Embed(title="Available Commands", color=discord.Color.blue())
    for command in bot.commands:
        if command.brief:
            embed.add_field(name=f"!{command.name}", value=command.description, inline=False)
    await ctx.send(embed=embed)

# !ping
@bot.hybrid_command(
    name='ping',
    brief='Check bot latency',
    description='Check bot latency in milliseconds',
)
async def ping(ctx):
    await ctx.send(str(round(bot.latency * 1000)) + "ms")

async def get_first_youtube_result(query):
    videos_search = VideosSearch(query, limit=1)
    result = videos_search.result()
    if result['result']:
        return result['result'][0]['link']
    return None

# !play <query>
@bot.hybrid_command(
    name='play',
    aliases=['p'],
    brief='Play music from YouTube',
    description='Plays music from YouTube'
)
async def play(ctx, *, query: str):
    if not query:
        await ctx.send("No query provided.")
        return
    if not ctx.author.voice.channel:
        await ctx.send("You are not connected to a voice channel.")
        return

    channel = ctx.author.voice.channel
    filename = await download_youtube_video(query)

    if ctx.voice_client:
        vc = ctx.voice_client
        if vc.is_playing():
            vc.stop()
        vc.play(discord.FFmpegPCMAudio(filename))
    else:
        vc = await channel.connect()
        vc.play(discord.FFmpegPCMAudio(filename))

queueList = []
# !queue_add <query>
@bot.hybrid_command(
    name='queue_add',
    brief='Add a song to the queue',
    description='Add a song to the queue'
)
async def queue_add(ctx, *, query: str):
    link = await get_first_youtube_result(query)
    if link:
        queueList.append(link)
        await ctx.send("Added to queue.")
    else:
        await ctx.send("No results found.")

# !queue
@bot.hybrid_command(
    name='queue',
    brief='Show the queue',
    description='Show the queue'
)
async def queue(ctx):
    embed = discord.Embed(title="Queue", color=discord.Color.blue())
    if queueList:
        for i, link in enumerate(queueList):
            embed.add_field(name="", value=str(i+1) + ". " + link, inline=False)
        await ctx.send(embed=embed)
    else:
        embed.add_field(name="", value="Queue is empty.", inline=False)
        await ctx.send(embed=embed)

# !seek <time>
@bot.hybrid_command(
    name='seek',
    brief='Seek to a specific time',
    description='Seek to a specific time'
)
async def seek(ctx, time: int):
    vc = ctx.voice_client
    vc.source = discord.PCMVolumeTransformer(vc.source)
    vc.source.seek(time)

# !skip
@bot.hybrid_command(
    name='skip',
    brief='Skip the current song',
    description='Skip the current song'
)
async def skip(ctx):
    if queueList:
        link = queueList.pop(0)
        filename = await download_youtube_video(link)
        vc = ctx.voice_client
        vc.stop()
        vc.play(discord.FFmpegPCMAudio(filename))
        embed = discord.Embed(title="Skipped song", color=discord.Color.blue())
        await ctx.send(embed=embed)

# !yt <query>
@bot.hybrid_command(
    name='yt',
    brief='Search YouTube for a video',
    description='Search YouTube for a video'
)
async def yt(ctx, *, query: str):
    link = await get_first_youtube_result(query)
    if link:
        await ctx.send(link)
    else:
        await ctx.send("No results found.")

# !leave
@bot.hybrid_command(
    name='leave',
    aliases=['disconnect'],
    brief='Leave the voice channel',
    description='Leave the voice channel'
)
async def leave(ctx):
    vc = ctx.voice_client
    if vc:
        vc.stop()
        await vc.disconnect()
        embed = discord.Embed(title="Disconnected", color=discord.Color.blue())
        await ctx.send(embed=embed)

@bot.event
async def is_queue():
    if queueList and not vc.is_playing():
        link = queueList.pop(0)
        filename = await download_youtube_video(link)
        vc = bot.voice_clients[0]
        vc.play(discord.FFmpegPCMAudio(filename), after=is_queue)

jajco_count = 0

@bot.event
async def on_message(message):
    global jajco_count
    if bot.user.mentioned_in(message):
        print("Mentioned")
        await message.channel.send("SHUT THE FUCK UP")
    if "jajco" in message.content.lower():
        jajco_count += 1
        await message.channel.send("Ilość jajec: " + str(jajco_count))
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print("Syncing commands...")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

bot.run(BOT_TOKEN)