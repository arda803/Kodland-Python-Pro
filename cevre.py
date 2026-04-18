import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

atik_veri = {
    "plastik sise": {
        "sure": "450 yıl",
        "resim": r"C:\Users\Arda\Desktop\HER ŞEY\Kodlama\Pytyhon Pro\M2L2\Çevre\plasticbottle_og.jpeg", 
        "bilgi": "Plastikler mikroplastiklere ayrılarak deniz canlılarına zarar verir."
    },
    "cam sise": {
        "sure": "4000 yıl",
        "resim": r"C:\Users\Arda\Desktop\HER ŞEY\Kodlama\Pytyhon Pro\M2L2\Çevre\bottle_og.webp",
        "bilgi": "Cam sonsuz kez geri dönüştürülebilir, çöpe atmak yerine geri dönüşüme vermek en sağlıklısıdır."
    },
    "kagit": {
        "sure": "2-6 ay",
        "resim": r"C:\Users\Arda\Desktop\HER ŞEY\Kodlama\Pytyhon Pro\M2L2\Çevre\paper_og.jpg",
        "bilgi": "Kağıt doğada hızlıca çözünür, ancak geri dönüşümle ağaçların kesilmesini azaltır."
    },
    "aluminyum kutu": {
        "sure": "100-300 yıl",
        "resim": r"C:\Users\Arda\Desktop\HER ŞEY\Kodlama\Pytyhon Pro\M2L2\Çevre\aluminumcan_og.jpg",
        "bilgi": "Alüminyum kutular geri dönüştürülebilir, ancak doğada uzun süre kalır."
    },
}

@bot.event
async def on_ready():
    print(f'{bot.user} adıyla giriş yapıldı!')
@bot.command()
async def help(ctx):
    yardim_mesaji = """
    **Kullanılabilir Komutlar:**

    `!atik <madde>` - Bir atığın doğada yok olma süresini ve bilgilerini gösterir

    **Örnek:** `!atik plastik şişe`

    **Sorgulayabileceğin maddeler:**
    plastik şişe
    cam şişe  
    kağıt
    alüminyum kutu
    """
    await ctx.send(yardim_mesaji)
@bot.command()
async def atik(ctx, *, madde: str):
    tur = madde.lower()
    
    if tur in atik_veri:
        veri = atik_veri[tur]
        
        mesaj = (f"**Madde:** {tur.upper()}\n"
                 f"**Yok Olma Süresi:** {veri['sure']}\n"
                 f"**Bilgi:** {veri['bilgi']}")
        
        if os.path.exists(veri["resim"]):
            file = discord.File(veri["resim"], filename="atik_resmi.png")
            await ctx.send(content=mesaj, file=file)
        else:
            await ctx.send(content=mesaj + "\n*(Resim dosyası belirtilen yolda bulunamadı!)*")
    else:
        secenekler = ", ".join(atik_veri.keys())
        await ctx.send(f"'{madde}' listemizde yok. Deneyebileceğin seçenekler: {secenekler}")

bot.run('')
