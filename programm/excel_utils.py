from collections import Counter
from functools import reduce

import xlrd
import xlwt
from xlutils.copy import copy


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
    e = marks_count[5] / len(class_marks)*100 # "5"
    g = marks_count[4] / len(class_marks)*100 # "4"
    s = marks_count[3] / len(class_marks)*100 # "3"
    p = sum((e, g, s))  # plus marks

    print(e, g, s, p, q)
    if e > 50 and p >= 95 and q >= 80:
        return '5'
    elif e+g > 50 and p >= 90 and q>= 75:
        return '4'
    elif p >= 85 and q>= 70:
        return '3'
    else:
        return '2'
    

def save_file(data):
    book = xlrd.open_workbook('programm/template.xls',
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
    print(class_marks)

    # outcome
    # students quantity
    ws.write(32, 2, len(data['results']), STYLE_CENTER)
    ws.write(32, 4, round(len(data['results']) / 20 * 100, 1), STYLE_CENTER)
    # all-marks-student quantity
    ws.write(33, 2, len(class_marks), STYLE_CENTER)
    quantity = round(len(class_marks) / len(data['results'])*100, 1)
    ws.write(33, 4, quantity, STYLE_CENTER)
    # marks species
    marks_count = Counter(class_marks)
    excellent = marks_count[5]
    good = marks_count[4]
    satisfactory = marks_count[3]
    unsatisfactory = marks_count[2]

    ws.write(35, 2, excellent, STYLE_CENTER)
    ws.write(35, 4, round(excellent / len(class_marks) * 100, 1), STYLE_CENTER)
    ws.write(36, 2, good, STYLE_CENTER)
    ws.write(36, 4, round(good / len(class_marks) * 100, 1), STYLE_CENTER)
    ws.write(37, 2, satisfactory, STYLE_CENTER)
    ws.write(37, 4, round(satisfactory / len(class_marks) * 100, 1), STYLE_CENTER)
    ws.write(38, 2, unsatisfactory, STYLE_CENTER)
    ws.write(38, 4, round(unsatisfactory /
                          len(class_marks) * 100, 1), STYLE_CENTER)
    plus_marks = sum((excellent, good, satisfactory))
    ws.write(39, 2, plus_marks, STYLE_CENTER)
    ws.write(39, 4, round(plus_marks / len(class_marks) * 100, 1), STYLE_CENTER)
    ws.write(40, 2, len(data['results'])-len(class_marks), STYLE_CENTER)
    ws.write(40, 4, round(
        (len(data['results']) - len(class_marks)) / len(data['results'])* 100, 1), STYLE_CENTER)
        
    class_mark = calculate_class_mark(quantity, class_marks)
    ws.write(36, 7, class_mark, STYLE_BIG)

    try:
        wb.save('new.xls')
    except:
        print('!!!CLOSE FILE!!!\n'*10)


if __name__ == "__main__":
    save_file({
        'school_name': 'ТПКУ',
        'period': '1 Period',
        'teacher': {
            'name': 'Матвеев М.И.',
            'rank': 'Старший лейтенант',
            'post': 'Преподаватель'
        },
        'class_name': '5 а',
        'group': '1 Курс (5 Класс)',
        'exercises': {
            'Упр. №3 Подтягивание': [['1 Курс (5 Класс)', ['13', '10', '8']], ['2 Курс (6 Класс)', ['15', '13', '11']]],
            'Упр. №29 Бег на 60м': [['1 Курс (5 Класс)', ['9.00', '10.5', '11.00']]],
            'Упр. №27 Бег на 1000м': [['1 Курс (5 Класс)', ['12:00', '12:30', '13:00']]],
        },
        'results': {
            'Васильев': {'Упр. №3 Подтягивание': '12', 'Упр. №29 Бег на 60м': 'Б', 'Упр. №27 Бег на 1000м': '4:50', },
            'Иванов': {'Упр. №3 Подтягивание': '32', 'Упр. №29 Бег на 60м': '10.4', 'Упр. №27 Бег на 1000м': '64:30', },
            'Кузнецов': {'Упр. №3 Подтягивание': '22', 'Упр. №29 Бег на 60м': '11.5', 'Упр. №27 Бег на 1000м': '23:10', },
            'Петров': {'Упр. №3 Подтягивание': '12', 'Упр. №29 Бег на 60м': '9.1', 'Упр. №27 Бег на 1000м': '12:30', },
            'Попов': {'Упр. №3 Подтягивание': '1', 'Упр. №29 Бег на 60м': '12.4', 'Упр. №27 Бег на 1000м': '11:40', },
            'Смирнов': {'Упр. №3 Подтягивание': '442', 'Упр. №29 Бег на 60м': '11.7', 'Упр. №27 Бег на 1000м': '12:40', },
            'Соколов': {'Упр. №3 Подтягивание': '2', 'Упр. №29 Бег на 60м': '8.4', 'Упр. №27 Бег на 1000м': '333:40', },
            'Табаков': {'Упр. №3 Подтягивание': '12', 'Упр. №29 Бег на 60м': '', 'Упр. №27 Бег на 1000м': '4:50', },
            'Иванов': {'Упр. №3 Подтягивание': '8', 'Упр. №29 Бег на 60м': '10.4', 'Упр. №27 Бег на 1000м': '4:30', },
            'Хабалов': {'Упр. №3 Подтягивание': '22', 'Упр. №29 Бег на 60м': '11.5', 'Упр. №27 Бег на 1000м': '23:10', },
            'Цапко': {'Упр. №3 Подтягивание': '9', 'Упр. №29 Бег на 60м': '9.8', 'Упр. №27 Бег на 1000м': '12:30', },
            'Чаадаев': {'Упр. №3 Подтягивание': '1', 'Упр. №29 Бег на 60м': '12.4', 'Упр. №27 Бег на 1000м': '11:40', },
            'Чепаев': {'Упр. №3 Подтягивание': '442', 'Упр. №29 Бег на 60м': '11.7', 'Упр. №27 Бег на 1000м': '12:40', },
            'Яковлев': {'Упр. №3 Подтягивание': '2', 'Упр. №29 Бег на 60м': '8.4', 'Упр. №27 Бег на 1000м': '3:40', }
        }
    }
    )
