# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 16:00:22 2020

@author: kachnicka
"""

import os
import discord
import random

from dotenv import load_dotenv
from datetime import datetime, timedelta
from discord.ext import commands
from tabulate import tabulate

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OWNER = os.getenv('OWNER_ID')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.get_user(int(OWNER)).send('I am ready')

def is_eligible_to_whip():
    async def predicate(ctx):
        vedeniRole = await commands.RoleConverter().convert(ctx, 'vedeni')
        return vedeniRole in ctx.author.roles
    return commands.check(predicate)

async def getUnsignedRaiders(ctx):
    lookBackInDays = { 0 : 1, 1 : 2, 2 : 1, 3 : 2, 4 : 1, 5 : 2, 6 : 3 }
    now = datetime.utcnow()
    after = now - timedelta(days = lookBackInDays[now.weekday()], hours = now.hour)

    raiderRole = await commands.RoleConverter().convert(ctx, 'raider')
    allRaiders = set(raiderRole.members)
    unsignedRaiders = set()
    
    async for msg in ctx.channel.history(after=after):
        if msg.author.name == 'Raid-Helper':
            signedUsersSet = set()
            for r in msg.reactions:
                signedUsersSet.update(set(await r.users().flatten()))

            signedRaidersSet = set()
            for u in signedUsersSet:
                signedMember = ctx.guild.get_member(u.id)
                if raiderRole in signedMember.roles:
                    signedRaidersSet.add(signedMember)          

            unsignedRaiders.update(allRaiders.difference(signedRaidersSet))
    
    return unsignedRaiders

async def getUnsignedRaidersMsg(ctx, mention=True):
    unsignedRaiders = await getUnsignedRaiders(ctx)
    if not unsignedRaiders:
        msg = 'Everyone is signed. As the master wishes.'
    else:
        msg = 'Hmmm, you\'re in trouble now. Sign for raid!\n'
    for ur in unsignedRaiders:
        msg += ur.mention if mention else ur.display_name + ' '
        
    return msg
    
@bot.command(name='whipHere', help='Whip lash all unsigned members in this channel\'s recent events.')
@is_eligible_to_whip()
async def whipHere(ctx):
    msg = await getUnsignedRaidersMsg(ctx)

    await ctx.message.delete()
    await ctx.send(msg)
    
@bot.command(name='whipHereTest', help='Whip lash all unsigned members in this channel\'s recent events. Sent as DM.')
@is_eligible_to_whip()
async def whipHereTest(ctx):
    msg = await getUnsignedRaidersMsg(ctx, mention=False)

    await ctx.message.delete()
    await ctx.author.send(msg)
    
@whipHere.error
async def whipHere_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.message.delete()
        
@bot.command(name='t', help='test')
async def t(ctx):
    await ctx.send('I am here.')

def ListDiff(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))

@bot.command(name='newCouncil', help='Generate new loot council based on discord ranks.')
@is_eligible_to_whip()
async def newCouncil(ctx):    
    vedeni = (await commands.RoleConverter().convert(ctx, 'vedeni')).members
    core = ListDiff((await commands.RoleConverter().convert(ctx, 'raider')).members, vedeni)

    councilRoleSize = 9
    cVedeni = random.sample(vedeni, k=councilRoleSize)
    cCore = random.sample(core, k=councilRoleSize)
    
    council = []
    for n in range(councilRoleSize):
        if n == 2:
            row = [cVedeni[n].display_name, '']
        elif n == 3:
            row = ['', '']
        else:
            row = [cVedeni[n].display_name, cCore[n].display_name]
        council.append(row)
    
    table = tabulate(council, headers=["Vedeni", "CoreRaiders"])
    msg = '```New loot council \n\n' + table + '```'
 
    await ctx.message.delete()
    await ctx.send(msg)    
        
bot.run(TOKEN)
#    bot.send_message(bot.get_user(OWNER), 'I am dead')






























