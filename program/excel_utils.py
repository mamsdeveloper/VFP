__all__ = ['save_file', 'load_file']

import os
import sys
from collections import Counter
from functools import reduce

import xlrd
import xlwt
from xlutils.copy import copy


APP_DIR = sys.path[0] or os.path.dirname(
    os.path.realpath(sys.argv[0])) or os.getcwd()

FONT_USUAL = xlwt.Font()
FONT_USUAL.name = 'Times New Roman'
FONT_USUAL.height = 280  # 14

FONT_BIG = xlwt.Font()
FONT_BIG.name = 'Times New Roman'
FONT_BIG.height = 960  # 14

BOARDERS = xlwt.Formatting.Borders()
BOARDERS.left = BOARDERS.THIN
BOARDERS.left_colour = 0
BOARDERS.right = BOARDERS.THIN
BOARDERS.right_colour = 0
BOARDERS.top = BOARDERS.THIN
BOARDERS.top_colour = 0
BOARDERS.bottom = BOARDERS.THIN
BOARDERS.bottom_colour = 0

# Styles
HALIGN_CENTER = xlwt.Alignment()
HALIGN_CENTER.horz = xlwt.Alignment.HORZ_CENTER
STYLE_CENTER = xlwt.XFStyle()
STYLE_CENTER.alignment = HALIGN_CENTER
STYLE_CENTER.font = FONT_USUAL
STYLE_CENTER.borders = BOARDERS

HALIGN_LEFT = xlwt.Alignment()
HALIGN_LEFT.horz = xlwt.Alignment.HORZ_LEFT
STYLE_LEFT = xlwt.XFStyle()
STYLE_LEFT.alignment = HALIGN_LEFT
STYLE_LEFT.font = FONT_USUAL
STYLE_LEFT.borders = BOARDERS

ALIGNT_CENTER = xlwt.Alignment()
ALIGNT_CENTER.horz = xlwt.Alignment.HORZ_CENTER
ALIGNT_CENTER.vert = xlwt.Alignment.VERT_CENTER
STYLE_BIG = xlwt.XFStyle()
STYLE_BIG.alignment = ALIGNT_CENTER
STYLE_BIG.font = FONT_BIG
STYLE_BIG.borders = BOARDERS


def calculate_exercise_mark(result, standart):
    # in Sec.mSec
    try:
        if '.' in result:
            # prepare
            Sec, mSec = map(int, result.split('.'))
            result = Sec*10 + mSec
            pre_standart = []
            for i in range(3):
                Sec, mSec = map(int, standart[i].split('.'))
                pre_standart.append(Sec*10 + mSec)

            if result <= pre_standart[0]:
                return '5'
            elif result <= pre_standart[1]:
                return '4'
            elif result <= pre_standart[2]:
                return '3'
            else:
                return '2'
        # in Min:Sec
        elif ':' in result:
            # prepare
            Min, Sec = map(int, result.split(':'))
            result = Min*60 + Sec
            pre_standart = []
            for i in range(3):
                Min, Sec = map(int, standart[i].split(':'))
                pre_standart.append(Min*60 + Sec)

            if result <= pre_standart[0]:
                return '5'
            elif result <= pre_standart[1]:
                return '4'
            elif result <= pre_standart[2]:
                return '3'
            else:
                return '2'
        # in Times
        else:
            if int(result) >= int(standart[0]):
                return '5'
            elif int(result) >= int(standart[1]):
                return '4'
            elif int(result) >= int(standart[2]):
                return '3'
            else:
                return '2'
    except:
        print('Cant marking', result)
        return ''


def calculate_total_mark(marks):
    marks = list(map(int, marks))
    if len(marks) == 3:
        if reduce(lambda a, b: a*b, marks) >= 100:
            return '5'
        elif reduce(lambda a, b: a*b, marks) >= 60:
            return '4'
        elif reduce(lambda a, b: a * b, marks) >= 20:
            return '3'
        else:
            return '2'
    else:
        return ''


def calculate_class_mark(q, class_marks):
    marks_count = Counter(class_marks)
    e = marks_count[5] / len(class_marks)*100 if len(class_marks) else 0  # "5"
    g = marks_count[4] / len(class_marks)*100 if len(class_marks) else 0  # "4"
    s = marks_count[3] / len(class_marks)*100 if len(class_marks) else 0  # "3"
    p = sum((e, g, s))  # plus marks

    if e > 50 and p >= 95 and q >= 80:
        return '5'
    elif e+g > 50 and p >= 90 and q >= 75:
        return '4'
    elif p >= 85 and q >= 70:
        return '3'
    else:
        return '2'


def save_file(data, path, filename):
    book = xlrd.open_workbook(os.path.join(APP_DIR, 'template.xls'),
                              on_demand=True, formatting_info=True)
    wb = copy(book)
    ws = wb.get_sheet('Ведомость ФК')

    # school name
    ws.write(0, 0, data['school_name'], STYLE_CENTER)
    # period
    ws.write(3, 0, data['period'], STYLE_CENTER)
    # class
    ws.write(4, 0, data['class_name']+' класс', STYLE_CENTER)
    # teacher
    ws.write(42, 0, data['teacher']['post'], STYLE_CENTER)
    line = data['teacher']['rank']+' ' + '_'*12+' '+data['teacher']['name']
    ws.write(43, 0, line, STYLE_CENTER)
    # Exercises info
    class_marks = []
    for i, exercise in enumerate(data['exercises'].items()):
        exercise_number = ' '.join(exercise[0].split()[:2])
        exercise_name = ' '.join(exercise[0].split()[2:])
        standarts = [standart for standart in exercise[1]
                     if standart[0] == data['group']][0][1]

        ws.write(6, 2 + i * 2, exercise_number, STYLE_CENTER)
        ws.write(7, 2 + i * 2, exercise_name, STYLE_CENTER)
        ws.write(8, 2 + i * 2, '-'.join(standarts), STYLE_CENTER)

    for i, result in enumerate(data['results'].items()):
        ws.write(10 + i, 1, result[0], STYLE_LEFT)
        marks = []
        for j, exercise in enumerate(result[1].items()):
            if not exercise[1]:
                continue

            exercise_standart = [standart for standart in data['exercises']
                                 [exercise[0]] if standart[0] == data['group']][0][1]

            mark = calculate_exercise_mark(exercise[1], exercise_standart)

            if mark:
                marks.append(mark)
            ws.write(10 + i, 2 + j * 2, exercise[1], STYLE_CENTER)
            ws.write(10 + i, 3 + j * 2, mark, STYLE_CENTER)

        total_mark = calculate_total_mark(marks)
        class_marks.append(total_mark)
        ws.write(10 + i, 8, total_mark, STYLE_CENTER)

    class_marks = list(map(int, [mark for mark in class_marks if mark]))

    # outcome
    # students quantity
    ws.write(32, 2, len(data['results']), STYLE_CENTER)
    ws.write(32, 4, round(len(data['results']) / 20 * 100, 1), STYLE_CENTER)
    # all-marks-student quantity
    ws.write(33, 2, len(class_marks), STYLE_CENTER)
    quantity = round(len(class_marks) /
                     len(data['results'])*100, 1) if len(data['results']) else 0
    ws.write(33, 4, quantity, STYLE_CENTER)
    # marks species
    marks_count = Counter(class_marks)
    excellent = marks_count[5]
    good = marks_count[4]
    satisfactory = marks_count[3]
    unsatisfactory = marks_count[2]

    ws.write(35, 2, excellent, STYLE_CENTER)
    value = excellent / len(class_marks) * 100 if len(class_marks) else 0
    ws.write(35, 4, round(value, 1), STYLE_CENTER)

    ws.write(36, 2, good, STYLE_CENTER)
    value = good / len(class_marks) * 100 if len(class_marks) else 0
    ws.write(36, 4, round(value, 1), STYLE_CENTER)

    ws.write(37, 2, satisfactory, STYLE_CENTER)
    value = satisfactory / len(class_marks) * 100 if len(class_marks) else 0
    ws.write(37, 4, round(value, 1), STYLE_CENTER)

    ws.write(38, 2, unsatisfactory, STYLE_CENTER)
    value = unsatisfactory / len(class_marks) * 100 if len(class_marks) else 0
    ws.write(38, 4, round(value, 1), STYLE_CENTER)

    plus_marks = sum((excellent, good, satisfactory))
    ws.write(39, 2, plus_marks, STYLE_CENTER)
    value = plus_marks / len(class_marks) * 100 if len(class_marks) else 0
    ws.write(39, 4, round(value, 1), STYLE_CENTER)

    ws.write(40, 2, len(data['results']) - len(class_marks), STYLE_CENTER)
    value = (len(data['results']) - len(class_marks)) / \
        len(data['results']) * 100 if len(class_marks) else 0
    ws.write(40, 4, round(value, 1), STYLE_CENTER)

    class_mark = calculate_class_mark(quantity, class_marks)
    ws.write(36, 7, class_mark, STYLE_BIG)

    try:
        name = filename + '.xls' if filename else 'new.xls'
        wb.save(os.path.join(APP_DIR, '/'.join((path, name))))
        return True
    except PermissionError:
        return False
        print('!!!CLOSE FILE!!!')


def load_file(path):
    wb = xlrd.open_workbook(path)
    ws = wb.sheet_by_index(0)

    # school name
    school_name = ws.cell(0, 0).value
    # period
    period = ws.cell(3, 0).value
    # class
    class_name = ws.cell(4, 0).value
    # teacher
    teacher_post = ws.cell(42, 0).value
    try:
        teacher_rank, teacher_name = ws.cell(43, 0).value.split(' ' + '_' * 12 + ' ')
    except ValueError:
        teacher_rank, teacher_name = '', ''
        
    teacher = {
        'name': teacher_name.strip(),
        'post': teacher_post.strip(),
        'rank': teacher_rank.strip()
    }
    # exercises
    exercises = []
    for i in range(2, 6+1, 2):
        exercise_name = ' '.join((ws.cell(6, i).value, ws.cell(7, i).value))
        exercises.append(exercise_name)
    # results
    results = {}
    for i in range(10, 30 + 1):
        if value := ws.cell(i, 1).value:
            results.update({value: {}})
            for j in range(2, 6 + 1, 2):
                results[value].update({exercises[j//2-1]: ws.cell(i, j).value})

    return {
        'school_name': school_name,
        'period': period,
        'teacher': teacher,
        'class_name': class_name,
        'exercises': exercises,
        'results': results,
    }

