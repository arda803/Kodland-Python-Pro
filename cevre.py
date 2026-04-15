import discord
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
atik_veri = {
    "plastik sise": {
        "sure": "450 yıl",
        "resim": "", 
        "bilgi": "Plastikler mikroplastiklere ayrılarak deniz canlılarına zarar verir."
    },
    "cam sise": {
        "sure": "4000 yıl",
        "resim": "C:\\Users\\Arda\\Desktop\\HER ŞEY\\Kodlama\\Pytyhon Pro\\M2L2\\Çevre\\bottle_og.webp",
        "bilgi": "Cam sonsuz kez geri dönüştürülebilir, çöpe atmak yerine geri dönüşüme vermek en sağlıklısıdır."
    },
    "kagit": {
        "sure": "2-5 ay",
        "resim": "C:\\Users\\Arda\\Desktop\\HER ŞEY\\Kodlama\\Pytyhon Pro\\M2L2\\Çevre\\paper_og.webp",
        "bilgi": "Kağıt hızlı ayrışsa da ağaçları korumak için geri dönüşüm çok önemlidir."
    },
    "aluminyum kutu": {
        "sure": "200 yıl",
        "resim": "C:\\Users\\Arda\\Desktop\\HER ŞEY\\Kodlama\\Pytyhon Pro\\M2L2\\Çevre\\aluminum_can_og.webp",
        "bilgi": "Metallerin geri dönüştürülmesi, madencilikten %95 daha az enerji harcar."
    }
}
@bot.event
async def on_ready():
    print(f'Bot {bot.user} olarak giriş yaptı!')
@bot.command()
async def atik(ctx, atik_turu: str):
    """İstenilen atığın ayrışma süresini ve bilgileri verir."""
    atik = atik_turu.lower()
    if atik in atik_veri:
        sure = atik_veri[atik]["sure"]
        resim = atik_veri[atik]["resim"]  
        bilgi = atik_veri[atik]["bilgi"]

        embed = discord.Embed(title=f"Madde: {atik.capitalize()}", color=discord.Color.green())
        embed.add_field(name="Doğada Yok Olma Süresi", value=sure, inline=False)
        embed.add_field(name="Biliyor muydun?", value=bilgi, inline=False)
        embed.set_image(url=resim)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Maalesef bu madde listede yok. Şunları deneyebilirsin: " + ", ".join(atik_veri.keys()))
bot.run('')
