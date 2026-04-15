import os
import random
import discord
import requests 
from discord.ext import commands

# Bot ayarları
intents = discord.Intents.default()
intents.message_content = True  

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı!')

@bot.command()
async def mem(ctx):
    try:
        files = os.listdir("images")
        selected = random.choice(files)
        file_path = os.path.join("images", selected)
        with open(file_path, "rb") as f:
            picture = discord.File(f)
        await ctx.send(file=picture)
    except FileNotFoundError:
        await ctx.send("Hata: Bilgisayarda 'images' adında bir klasör bulunamadı")

def get_fox_image_url():    
    url = 'https://randomfox.ca/floof/'
    res = requests.get(url) 
    data = res.json()       
    return data['image'] 

@bot.command('tilki')
async def tilki(ctx):
    image_url = get_fox_image_url()
    await ctx.send(image_url)
bot.run("")
print("Bot başlatıldı!")