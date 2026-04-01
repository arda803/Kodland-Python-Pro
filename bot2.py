import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yaptık')
@bot.command()
async def multiply(ctx, left: int, right: int):
    """Multiplies two numbers."""
    await ctx.send(left * right)
@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)
@bot.command()
async def substract(ctx, left: int, right: int):
    """Substracts two numbers."""
    await ctx.send(left - right)
@bot.command()
async def divide(ctx, left: int, right: int):
    """Divides two numbers."""
    if right == 0:
        await ctx.send("Sayıları sıfıra bölmezsin")
    else:
        await ctx.send(left / right)
@bot.command()
async def hello(ctx):
    await ctx.send(f'Merhaba! Ben {bot.user}, bir Discord sohbet botuyum!')

@bot.command()
async def heh(ctx, count_heh = 5):
    await ctx.send("he" * count_heh)

bot.run("MTQ4NjQ0Nzg5NzcwMzg3NDgxMg.Gmwpdg.yMhEBHvAqVTRa3VWWsw7cBbXrK7g4MYjqdHgso")