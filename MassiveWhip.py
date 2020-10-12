# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 16:00:22 2020

@author: kachnicka
"""

import os
import discord

from dotenv import load_dotenv
from datetime import datetime, timedelta
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

def is_eligible_to_whip():
    async def predicate(ctx):
        eRole1 = await commands.RoleConverter().convert(ctx, 'vedeni')
        eRole2 = await commands.RoleConverter().convert(ctx, 'veteran')
        return eRole1 in ctx.author.roles or eRole2 in ctx.author.roles
    return commands.check(predicate)
    
@bot.command(name='whipHere', help='Whip lash all unsigned members in this channel\'s recent events.')
@is_eligible_to_whip()
async def whipHere(ctx):
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

    if not unsignedRaiders:
        ret = 'Everyone is signed. As the master wishes.'
    else:
        ret = 'Hmmm, you\'re in trouble now. Sign for raid!\n'
    for ur in unsignedRaiders:
        ret += ur.mention + ' '
        #ret += ur.display_name + ' '  

    await ctx.message.delete()
    await ctx.send(ret)
    
@whipHere.error
async def whipHere_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.message.delete()
        
bot.run(TOKEN)