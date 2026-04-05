# musicbot.py
# This example requires the 'message_content' privileged intent to function.

import os
import asyncio
import logging
from pathlib import Path

import discord
import yt_dlp as youtube_dl
from discord.ext import commands
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Logging
logging.basicConfig(level=logging.INFO)

# Suppress youtube-dl/yt-dlp bug report noise
youtube_dl.utils.bug_reports_message = lambda *args, **kwargs: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if data is None:
            raise RuntimeError("Yt-dlp returned no data for the URL")

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Her sunucu (guild) için ayrı bir müzik sırası tutacağımız sözlük
        self.queues = {}

    def get_queue(self, guild_id):
        """Belirtilen sunucu için kuyruğu getirir, yoksa oluşturur."""
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]

    def play_next(self, ctx):
        """Sıradaki şarkıya geçişi sağlar."""
        queue = self.get_queue(ctx.guild.id)
        if len(queue) > 0:
            next_query = queue.pop(0) # Sıradaki şarkıyı listeden al
            # Şarkıyı çalma işlemini asenkron olarak başlat
            self.bot.loop.create_task(self._play_song(ctx, next_query))
        else:
            # Sıra bittiyse yapılacak ekstra bir işlem buraya yazılabilir
            pass

    async def _play_song(self, ctx, query):
        """Arka planda şarkıyı çalan yardımcı fonksiyon."""
        try:
            # Hızlı olması için stream=True kullanıyoruz (indirme yapmaz)
            player = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
            
            # Şarkı bittiğinde play_next fonksiyonunu tetikliyoruz
            ctx.voice_client.play(player, after=lambda e: self.play_next(ctx))
            await ctx.send(f'🎵 Şimdi çalıyor: **{player.title}**')
        except Exception as e:
            logging.error(f"Player error: {e}")
            await ctx.send("Şarkı çalınırken bir hata oluştu, sıradakine geçiliyor...")
            self.play_next(ctx) # Hata olursa sıradakine geç

    @commands.command(name='join')
    async def join(self, ctx):
        """Botu bulunduğun ses kanalına çağırır."""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("Bir ses kanalında değilsin.")
            return

        channel = ctx.author.voice.channel
        permissions = channel.permissions_for(ctx.guild.me)
        
        if not permissions.connect or not permissions.speak:
            await ctx.send("Bu kanala bağlanma veya konuşma iznim yok.")
            return

        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()

        await ctx.send(f"{channel.name} kanalına katıldım!")

    @commands.command(name='leave', aliases=['disconnect', 'dc'])
    async def leave(self, ctx):
        """Botu ses kanalından çıkarır."""
        if ctx.voice_client is None:
            await ctx.send("Bot şu anda herhangi bir ses kanalında değil.")
            return
        
        self.get_queue(ctx.guild.id).clear() # Ayrılırken sırayı temizle
        await ctx.voice_client.disconnect()
        await ctx.send("Ses kanalından ayrıldım.")

    @commands.command(name='play', aliases=['p', 'çal'])
    async def play(self, ctx, *, query: str):
        """Şarkıyı sıraya ekler (Link veya isim yazabilirsiniz)."""
        queue = self.get_queue(ctx.guild.id)
        queue.append(query)
        await ctx.send(f'📥 Sıraya eklendi: **{query}**')

        # Eğer şu an bir şey çalmıyorsa veya duraklatılmadıysa sıradakini başlat
        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            self.play_next(ctx)

    @commands.command(name='skip', aliases=['atla', 's'])
    async def skip(self, ctx):
        """Şu an çalan şarkıyı atlar ve sıradakine geçer."""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            return await ctx.send("Şu anda çalan bir şarkı yok.")

        # ctx.voice_client.stop() komutu mevcut çalmayı durdurur. 
        # Durduğu an `after` parametresi tetiklenir ve otomatik olarak sıradaki şarkı başlar!
        ctx.voice_client.stop()
        await ctx.send("⏭️ Şarkı atlandı!")

    @commands.command(name='queue', aliases=['q', 'sıra'])
    async def queue_cmd(self, ctx):
        """Şu anki şarkı sırasını gösterir."""
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            return await ctx.send("Sıra şu anda boş.")
        
        # Sırayı formatlayıp mesaja dönüştür
        q_list = "\n".join([f"**{i+1}.** {query}" for i, query in enumerate(queue[:10])]) # İlk 10 şarkıyı gösterir
        
        if len(queue) > 10:
            q_list += f"\n*...ve {len(queue) - 10} şarkı daha.*"
            
        await ctx.send(f"📋 **Şarkı Sırası:**\n{q_list}")

    @commands.command(name='stop')
    async def stop(self, ctx):
        """Sırayı temizler ve botu tamamen durdurur."""
        if ctx.voice_client is None:
            return await ctx.send("Bot herhangi bir ses kanalında değil.")
            
        self.get_queue(ctx.guild.id).clear() # Sırayı sıfırla
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Sıra temizlendi, durdurdum ve kanaldan ayrıldım.")

    @commands.command(name='volume')
    async def volume(self, ctx, volume: int):
        """Ses seviyesini ayarlar (0-200)."""
        if ctx.voice_client is None or ctx.voice_client.source is None:
            return await ctx.send("Şu anda çalan bir şey yok.")

        if not 0 <= volume <= 200:
            return await ctx.send("Ses 0 ile 200 arasında olmalı.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"🔊 Ses seviyesi %{volume} olarak ayarlandı.")

    # Play komutundan önce bota kanala katılmasını sağlar
    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice and ctx.author.voice.channel:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("Önce bir ses kanalına gir veya !join kullan.")
                raise commands.CommandError("Author not connected to a voice channel.")


intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description='Relatively simple music bot example with queue',
    intents=intents,
)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    logging.info('------')

async def main():
    async with bot:
        await bot.add_cog(Music(bot))

        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            print("HATA: .env dosyasında DISCORD_BOT_TOKEN bulunamadı!")
            return
            
        await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())