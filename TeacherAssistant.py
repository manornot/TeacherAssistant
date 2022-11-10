from discord.ext.commands import CommandNotFound
from pydantic import BaseModel
import os
import discord
import re
from discord.ext import commands
import logging
import coloredlogs
import pathlib
import numpy as np
import json
from config import TOKEN


def namesSimilarity(name1: str, name2: str) -> int:
    score = 0
    for symbol1, symbol2 in zip(name1, name2):
        if symbol1 == symbol2:
            score += 1
    return score


class Student(BaseModel):
    name: str
    display_name: str
    student_id: int
    path_to_reviews: list[pathlib.PosixPath]


class studentAssignemt(BaseModel):
    name: pathlib.PosixPath
    std_id: str
    assignments: list[int] = []


class StudenIDMap(BaseModel):
    studentList: list[studentAssignemt] = []


assignment_path = pathlib.Path('/home/pi/TeacherAssistant/Assignments')
HW_path = pathlib.Path('/home/pi/TeacherAssistant/Students_HW')
botFolder = pathlib.Path('/home/pi/TeacherAssistant')
logger = logging.getLogger('TecherAssistant')
coloredlogs.install(level=logging.DEBUG, logger=logger,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ex_hw_file_format = 'PA\d_HW\d+_(?!review)\w+(\.\w+)$'
ex_review_file_format = 'PA\d_HW\d+_review_\d+(\.\w+)$'
#ex_hw_file_format = 'PA3_HW\d.*\.\w+$'
ex_extract_name = '(?<=PA3_HW\d+_).+(?=(\.\w+)$)'
intents = discord.Intents.default()
#intents.presences = True
#intents.members = True
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='/', intents=intents)


@client.event
async def on_ready():
    pass


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.channel.send(f'Unknown Command')
        await ctx.invoke(bot.get_command('help'))
        return


def testRole(author, awaitedRole: str) -> bool:
    if str(author.top_role) != awaitedRole:
        logger.warning(
            f'some nigga named {author} is trying to do some shit')
        logger.warning(
            f'nigga role is {author.top_role}, but the {awaitedRole} role is required')
        return False
    else:
        return True


def getAllTextChannelsInCategory(category: str, guild: discord.Guild) -> list[discord.abc.GuildChannel]:
    text_channel_list = []
    logger.debug(f'guild = {guild}')
    for channel in guild.channels:
        if channel.category:
            if channel.category.name == category:
                text_channel_list.append(channel)
    return text_channel_list


@bot.command(describe='downloads all homeworsk to server, available only for teachers')
async def download_homeworks(ctx, arg):
    if testRole(ctx.author, 'Teacher'):
        text_channel_list = getAllTextChannelsInCategory(
            'school work submission', ctx.guild)

        for channel in text_channel_list:
            async for msg in channel.history(limit=200):
                for attachment in msg.attachments:
                    if re.search(ex_hw_file_format, attachment.filename):
                        logger.debug(attachment.filename)
                        #logger.debug(f'Valid format')
                        folder_name = re.search(
                            ex_extract_name, attachment.filename)[0]
                        logger.info(f'folder name = {folder_name}')
                        if fld_nmbr := re.search('(?<=_)\d', folder_name):
                            folder_name = folder_name.replace(
                                f'_{fld_nmbr[0]}', '')
                            logger.info(f'new folder name = {folder_name}')

                        if arg in attachment.filename:
                            try:
                                if not pathlib.Path(botFolder.joinpath('Students_HW')).is_dir():
                                    pathlib.Path(botFolder.joinpath(
                                        'Students_HW')).mkdir()
                                if not pathlib.Path(botFolder.joinpath('Students_HW').joinpath(f'{arg}')).is_dir():
                                    pathlib.Path(botFolder.joinpath(
                                        'Students_HW').joinpath(f'{arg}')).mkdir()
                                if not pathlib.Path(botFolder.joinpath('Students_HW').joinpath(f'{arg}').joinpath(f'{folder_name}')).is_dir():
                                    pathlib.Path(botFolder.joinpath('Students_HW').joinpath(
                                        f'{arg}').joinpath(f'{folder_name}')).mkdir()
                            except:
                                pass
                            await attachment.save(f'{botFolder}/Students_HW/{arg}/{folder_name}/{attachment.filename}')
                            await ctx.channel.send(f'saving {attachment.filename}')
                            with open('homework_channels.txt', 'a+') as hw_chan:
                                hw_chan.write(f'{channel.name}\n')
                        # await channel.delete()
                    else:
                        pass
                        # await channel.send('Wrong File Name Format, next read course HW assignment subbmition rules')
                        # await channel.send(f'RegEx for checking file name: {ex_hw_file_format}')


@bot.command(describe='downloads all reviews to server, available only for teachers')
async def download_reviews(ctx, arg):
    if testRole(ctx.author, 'Teacher'):
        text_channel_list = getAllTextChannelsInCategory(
            'school work submission', ctx.guild)

        for channel in text_channel_list:
            async for msg in channel.history(limit=200):
                for attachment in msg.attachments:
                    if re.search(ex_review_file_format, attachment.filename):
                        logger.debug(attachment.filename)
                        #logger.debug(f'Valid format')
                        folder_name = f'{arg}_reviews'
                        logger.info(f'folder name = {folder_name}')
                        if fld_nmbr := re.search('(?<=_)\d', folder_name):
                            folder_name = folder_name.replace(
                                f'_{fld_nmbr[0]}', '')
                            logger.info(f'new folder name = {folder_name}')

                        if arg in attachment.filename:
                            if not pathlib.Path(botFolder.joinpath('Students_HW').joinpath(folder_name)).is_dir():
                                pathlib.Path(botFolder.joinpath(
                                    'Students_HW').joinpath(folder_name)).mkdir()
                            await attachment.save(f'{botFolder}/Students_HW/{folder_name}/from_{channel.id}_{attachment.filename}')
                            await ctx.channel.send(f'saving {attachment.filename} from {channel}')
                        # await channel.delete()
                    else:
                        pass
                        # await channel.send('Wrong File Name Format, next read course HW assignment subbmition rules')
                        # await channel.send(f'RegEx for checking file name: {ex_hw_file_format}')


@bot.command()
async def test_hw(ctx):
    async for msg in ctx.channel.history(limit=10):
        for attachment in msg.attachments:
            if attachment:
                await ctx.channel.send('Testing HW')
                if res := re.search(ex_hw_file_format, attachment.filename):
                    await ctx.channel.send(f'Your HW file looks fine, thats what i see \n {res[0]}')
                else:
                    await ctx.channel.send(f'Hey choom, there is smth wrong with your hw, read cearfully the course hw submittion rules')
                    await ctx.channel.send(f'to check your files your could use following regex')
                    await ctx.channel.send(f'```\n{ex_hw_file_format}\n```')
                logger.debug(f'{attachment.filename}')
                return


@bot.command()
async def test_review(ctx):
    good_attachment_count = 0
    bad_attachment_count = 0
    await ctx.channel.send('Testing reviews')
    async for msg in ctx.channel.history(limit=10):
        for attachment in msg.attachments:
            if attachment:

                if res := re.search(ex_review_file_format, attachment.filename):
                    # await ctx.channel.send(f'Your review file looks fine, thats what i see \n {res[0]}')
                    good_attachment_count += 1
                else:
                    bad_attachment_count += 1
                    # await ctx.channel.send(f'Hey choom, there is smth wrong with your hw, read cearfully the course hw submittion rules')
                logger.debug(f'{attachment.filename}')

                # return
    if bad_attachment_count:
        await ctx.channel.send(f'I found {bad_attachment_count} attachments in this channel that doesnt meet the review naming requiremnts, and {good_attachment_count}, that are fine, please close that ticket, read cearfullty review submittion rules in course channel and resubmitt your reviews in new ticket')
        await ctx.channel.send(f'to check your files your could use following regex')
        await ctx.channel.send(f'```\n{ex_review_file_format}\n```')
    else:
        await ctx.channel.send(f'All files are fine, i found {good_attachment_count} files')


@bot.command()
async def send_for_review(ctx, arg):
    logger.info(f'arg = {arg}')
    for directory in os.listdir(assignment_path.joinpath(arg)):
        logger.info(f'directory = {directory}')
        similarities = [namesSimilarity(directory.replace('_', ' '), member.display_name.replace(
            '_', ' ').replace('-', ' ')) for member in ctx.guild.members]
        logger.debug(
            f'we hope that {directory} is the same as {ctx.guild.members[np.argmax(similarities)].display_name}')
        files2send = [discord.File(assignment_path.joinpath(arg).joinpath(directory).joinpath(
            pth_to_file)) for pth_to_file in os.listdir(assignment_path.joinpath(arg).joinpath(directory))]
        await ctx.guild.members[np.argmax(similarities)].send(
            f'I hope i identified you properly, i see you as {directory} and hope that it is the same as {ctx.guild.members[np.argmax(similarities)].display_name}\n' +
            'if i identified you in wrong way, please ignore sent files and contact with course Teacher, he/she gonna send you assignments'
        )

        for file2send in files2send:
            logger.info(
                f'sending {file2send} to {ctx.guild.members[np.argmax(similarities)].display_name}')
            await ctx.channel.send(f'sending {file2send}')
            await ctx.guild.members[np.argmax(similarities)].send(file=file2send)

        # for member in ctx.guild.members:
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


# client.run(TOKEN)

@bot.command()
async def send_reviews_back(ctx, arg):
    logger.debug(f'looking for map of {arg}')
    with open(HW_path.joinpath(f'{arg}').joinpath(f'studen_map_{arg}'), 'r') as std_map:
        student_map = StudenIDMap(studentList=json.loads(
            std_map.read()).get('studentList'))

    student_list = []
    for stud in student_map.studentList:
        student_name = str(stud.name).split('/')[-2]
        student_list.append(
            Student(
                name=student_name,
                student_id=stud.std_id,
                display_name='',
                path_to_reviews=[]
            ))
    logger.debug(f'student list \n{student_list}')
    for review in HW_path.joinpath(f'{arg}_reviews').iterdir():
        logger.debug(f'review\n{review}')
        review_id = int(
            re.search(f'(?<=PA3_{arg}_review_)\d+', str(review))[0])
        logger.debug(f'review_id = {review_id}')
        logger.debug(
            f'users on server\n{[member.display_name for member in ctx.guild.members]}')
        for student in student_list:
            similarities = [namesSimilarity(student.name.replace('_', ' '), member.display_name.replace(
                '_', ' ').replace('-', ' ')) for member in ctx.guild.members]
            student.display_name = [member.display_name for member in ctx.guild.members][np.argmax(
                similarities)]

            if review_id == student.student_id:
                student.path_to_reviews.append(review)
    for student in student_list:
        for member in ctx.guild.members:
            if member.display_name == student.display_name:
                for file2send in student.path_to_reviews:
                    logger.debug(
                        f'sending {file2send} to {student.name}/{member.display_name}')
                    await ctx.channel.send(f'sending {file2send} to {student.name}/{member.display_name}')
                    await member.send(file=discord.File(file2send))


bot.run(TOKEN)
