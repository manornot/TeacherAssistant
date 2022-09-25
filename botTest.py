from distutils.log import debug
import os
import discord
import re
from discord.ext import commands
import logging
import coloredlogs
import pathlib
import numpy as np
from config import TOKEN

def namesSimilarity(name1:str,name2:str) -> int:
    score = 0
    for symbol1,symbol2 in zip(name1,name2):
        if symbol1 == symbol2:
            score+=1
    return score


assignment_path = pathlib.Path('/mnt/g/Other computers/PC/Drive/Ju/EDX/Python_coding/DiscordBot/Assignments')

logger = logging.getLogger('TecherAssistant')
coloredlogs.install(level=logging.DEBUG,logger = logger,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ex_hw_file_format = 'PA\d_HW\d_(?!review)\w+(\.\w+)$'
#ex_hw_file_format = 'PA3_HW\d.*\.\w+$'
ex_extract_name = '(?<=PA3_HW\d_).+(?=(\.\w+)$)'
intents = discord.Intents.default()
#intents.presences = True
#intents.members = True
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='/',intents=intents)

@client.event
async def on_ready():
    pass

@bot.command()
async def download_homeworks(ctx,arg):
    if ctx.author.top_role != '@everyone':
        logger.warning(f'some nigga named {ctx.author} is trying to do some shit')
    else:
        text_channel_list = []
        for guild in bot.guilds:
            for channel in guild.channels:
                if channel.category:
                    if channel.category.name == 'school work submission':
                        text_channel_list.append(channel)
        #msg = await discord.utils.get(channel.history())
        #logger.debug(f'channel list = {text_channel_list}')
        for channel in text_channel_list:
            async for msg in channel.history(limit=200):
                #print(msg.author.name)
                #print(dir(msg))
                for attachment in msg.attachments:
                    #print('attachment')
                    #logger.debug(attachment.filename)
                    if re.search(ex_hw_file_format,attachment.filename):
                        logger.debug(attachment.filename)
                        #logger.debug(f'Valid format')
                        folder_name = re.search(ex_extract_name,attachment.filename)[0]
                        logger.info(f'folder name = {folder_name}')
                        if fld_nmbr:=re.search('(?<=_)\d',folder_name):
                            folder_name = folder_name.replace(f'_{fld_nmbr[0]}','')
                            logger.info(f'new folder name = {folder_name}')

                        if arg in attachment.filename:
                            try:
                                os.mkdir(f'Students_HW/{folder_name}')
                            except:
                                pass
                            await attachment.save(f'Students_HW/{folder_name}/{attachment.filename}')
                            with open('homework_channels.txt','a+') as hw_chan:
                                hw_chan.write(f'{channel.name}\n')
                        #await channel.delete()
                    else:
                        pass
                        #await channel.send('Wrong File Name Format, next read course HW assignment subbmition rules')
                        #await channel.send(f'RegEx for checking file name: {ex_hw_file_format}')
        
            
@bot.command()
async def test_hw(ctx):
    async for msg in ctx.channel.history(limit=10):
        for attachment in msg.attachments:
            if attachment:
                await ctx.channel.send('Testing HW')
                if res:=re.search(ex_hw_file_format,attachment.filename):
                    await ctx.channel.send(f'Your HW file looks fine, thats what i see \n {res[0]}')
                else:
                    await ctx.channel.send(f'Hey choom, there is smth wrong with your hw, read cearfully the course hw submittion rules')
                logger.debug(f'{attachment.filename}')
                return 

@bot.command()
async def send_for_review(ctx):
    for directory in os.listdir(assignment_path):
            
            similarities = [namesSimilarity(directory.replace('_',' '),member.display_name.replace('_',' ').replace('-',' ')) for member in ctx.guild.members]
            logger.debug(f'we hope that {directory} is the same as {ctx.guild.members[np.argmax(similarities)].display_name}')
            files2send = [discord.File(assignment_path.joinpath(directory).joinpath(pth_to_file)) for pth_to_file in os.listdir(assignment_path.joinpath(directory))]
            await ctx.guild.members[np.argmax(similarities)].send(
                f'I hope i identified you properly, i see you as {directory} and hope that it is the same as {ctx.guild.members[np.argmax(similarities)].display_name}\n' +
                'if i identified you in wrong way, please ignore sent files and contact with course Teacher, he/she gonna send you assignments'
                )
            for file2send in files2send:
                await ctx.guild.members[np.argmax(similarities)].send(file=file2send)

        
        #for member in ctx.guild.members:
        #    mod_name = member.display_name
        #    logger.debug(f'{mod_name}')
        #    name = member.display_name.replace('_',' ')
        #    name = name.replace('-',' ')
#
        #    similarities = [namesSimilarity(name,directory.replace('_',' ')) for directory in os.listdir(assignment_path)]
        #    logger.debug(f'similarities = {similarities}')
        #    logger.debug(f'max = {max(similarities)}')
        #    logger.debug(f'arg_max = {np.argmax(similarities)}')
        #    logger.debug(f'we hope that {name} is the same as {os.listdir(assignment_path)[np.argmax(similarities)]}')
        
        
#client.run(TOKEN)
bot.run(TOKEN)