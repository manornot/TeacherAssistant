import logging
import coloredlogs
import pathlib
from pathlib import Path
import json
import re
import shutil
from pydantic import BaseModel
logger = logging.getLogger('main')
coloredlogs.install(logger=logger, level='DEBUG')


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


HW_path = Path('/home/pi/TeacherAssistant/Students_HW')

assignments_path = Path('/home/pi/TeacherAssistant/Assignments')

hw_nmbr = input(f'Enter HW number\n')

with open(HW_path.joinpath(f'{hw_nmbr}').joinpath(f'studen_map_{hw_nmbr}'), 'r') as std_map:
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

for review in HW_path.joinpath(f'{hw_nmbr}_reviews').iterdir():
    review_id = int(re.search(f'(?<=PA3_{hw_nmbr}_review_)\d', str(review))[0])
    logger.debug(f'{review_id}')
    for student in student_list:
        if review_id == student.student_id:
            student.path_to_reviews.append(review)
logger.debug(f'{student_list}')
# get all received reviews
# get review's id
# get student_ids from student_map
# get student_names from student_map
# get names from guild
# link review id with student id with student name with guild name
