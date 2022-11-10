from pydantic import BaseModel
from pathlib import Path
import pathlib
import shutil
import random
import os
from typing import List
import json
import logging
import coloredlogs
import re
import numpy as np

logger = logging.getLogger('main')
coloredlogs.install(logger=logger, level='DEBUG')


class studentAssignemt(BaseModel):
    name: pathlib.PosixPath
    std_id: str
    assignments: List[int] = []


class StudenIDMap(BaseModel):
    studentList: List[studentAssignemt] = []


HW_path = Path(
    "G:\Other computers\PC\Drive\Ju\EDX\Python_coding\DiscordBot\Students_HW")
HW_path = Path('/home/pi/TeacherAssistant/Students_HW')
assignments_path = Path(
    "G:\Other computers\PC\Drive\Ju\EDX\Python_coding\DiscordBot\Assignments")
assignments_path = Path(
    '/home/pi/TeacherAssistant/Assignments')

hw_nmbr = input('Enter HW number')

hws_folders = Path(HW_path).joinpath(f'{hw_nmbr}')
hws_fldrs_paths = []
hws_paths = []
for hw_fldr in hws_folders.iterdir():
    hws_fldrs_paths.append(hw_fldr)

for pth in hws_fldrs_paths:
    hws_paths.append([pth.joinpath(file) for file in pth.iterdir()])


try:
    shutil.rmtree(assignments_path.joinpath(hw_nmbr))
    logger.debug('previouse files are destroyed')
except:
    logger.debug('nothing to destroy')
    pass


assignments_path.joinpath(hw_nmbr).mkdir()
logger.debug('new directory is created')

for directory, pth_list, indx in zip(hws_fldrs_paths, hws_paths, range(len(hws_paths))):
    logger.debug(f'{directory},{pth_list}')
    if len(pth_list) > 1:
        fl_nm = shutil.make_archive(
            directory, format='zip', root_dir=directory)
        shutil.move(fl_nm, directory)
        file_name = fl_nm.split('/')[-1]
        hws_paths[indx] = [str(directory.joinpath(file_name))]


hws_folders = os.listdir(HW_path.joinpath(hw_nmbr))
for flrd in hws_folders:
    os.mkdir(assignments_path.joinpath(hw_nmbr).joinpath(f'{flrd}'))

random.shuffle(hws_paths)

student_id_map = StudenIDMap(studentList=[studentAssignemt(
    name=student[0], std_id=index) for index, student in enumerate(hws_paths)])

logger.debug('starting random assignment')

available_assignment_list = []
for sdnt in student_id_map.studentList:
    available_assignment_list.append([sdnt.std_id]*3)

available_assignment_list = np.asanyarray(available_assignment_list)

for indx, student in enumerate(student_id_map.studentList):
    probability_list = np.asanyarray(
        [1/len(np.unique(available_assignment_list))]*len(np.unique(available_assignment_list)))
    logger.debug(f'probability sum = {np.sum(probability_list)}')
    probability_list[indx] = 0
    probability_list[probability_list >
                     0] += (1-np.sum(probability_list))/(len(probability_list)-1)
    logger.debug(f'probability sum = {np.sum(probability_list)}')
    student.assignments = list(np.random.choice(
        np.unique(available_assignment_list), 3, replace=False, p=probability_list))
"""
for student in student_id_map.studentList:
    for i in range(3):
        prey = random.choice(student_id_map.studentList)
        counter = 0
        while prey.std_id == student.std_id or len(prey.assignments) >= 3 or student.std_id in prey.assignments:
            if any([len(std_ass.assignments) < 3 for std_ass in student_id_map.studentList]) and counter < 50:
                prey = random.choice(student_id_map.studentList)
                counter += 1
            else:
                break
        if len(prey.assignments) < 3:
            prey.assignments.append(student.std_id)
"""
logger.debug('random assignemnt is over')

logger.debug('saving id map to file')
for stud in student_id_map.studentList:
    stud.name = str(stud.name)
pathToMap = HW_path.joinpath(hw_nmbr).joinpath(f'studen_map_{hw_nmbr}')
with open(pathToMap, 'w+') as f:
    f.write(json.dumps(student_id_map.dict(), indent=2))

logger.debug('map is saved')

logger.debug('starting copy procedure')

for stud in student_id_map.studentList:
    for assignmnt in stud.assignments:
        for stud_1 in student_id_map.studentList:
            if stud_1.std_id == assignmnt:
                hw_source = stud_1.name
                break
        file_extension = re.search('\.\w+$', hw_source)[0]
        file_name = hw_source.split('/')[-1]
        dir_name = stud.name.split('/')[-2]
        logger.debug(
            f'file name = {file_name}, file extension = {file_extension},')
        hw_dest = assignments_path.joinpath(hw_nmbr).joinpath(
            dir_name).joinpath(f'{assignmnt}{file_extension}')
        shutil.copy2(hw_source, hw_dest)
logger.debug('copy procedure done')
