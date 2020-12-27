import xlrd
import xlwt
from functools import reduce
from xlutils.copy import copy

FONT = xlwt.Font()
FONT.name = 'Times New Roman'
FONT.height = 280  # 14


def calculate_exercise_mark(result, standart):
    # in Sec.mSec
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
        if result >= standart[0]:
            return '5'
        elif result >= standart[1]:
            return '4'
        elif result >= standart[2]:
            return '3'
        else:
            return '2' 
        

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


def save_file(data):
    book = xlrd.open_workbook('programm/template.xls',
                              on_demand=True, formatting_info=True)
    wb = copy(book)
    ws = wb.get_sheet('Ведомость ФК')

    # Styles
    align_center = xlwt.Alignment()
    align_center.horz = xlwt.Alignment.HORZ_CENTER
    style_center = xlwt.XFStyle()
    style_center.alignment = align_center
    style_center.font = FONT

    align_left = xlwt.Alignment()
    align_left.horz = xlwt.Alignment.HORZ_LEFT
    style_left = xlwt.XFStyle()
    style_left.alignment = align_left
    style_left.font = FONT

    # school name
    ws.write(0, 0, data['school_name'], style_center)
    # period
    ws.write(3, 0, data['period'], style_center)
    # class
    ws.write(4, 0, data['class_name']+' класс', style_center)
    # teacher
    ws.write(42, 0, data['teacher']['post'], style_center)
    line = data['teacher']['rank']+' ' + '_'*12+' '+data['teacher']['name']
    ws.write(43, 0, line, style_center)
    # Exercises info
    for i, exercise in enumerate(data['exercises'].items()):
        exercise_number = ' '.join(exercise[0].split()[:2])
        exercise_name = ' '.join(exercise[0].split()[2:])
        standarts = [standart for standart in exercise[1]
                     if standart[0] == data['group']][0][1]

        ws.write(6, 2 + i * 2, exercise_number, style_center)
        ws.write(7, 2 + i * 2, exercise_name, style_center)
        ws.write(8, 2 + i * 2, '-'.join(standarts), style_center)

    for i, result in enumerate(data['results'].items()):
        ws.write(10 + i, 1, result[0], style_left)
        marks = []
        for j, exercise in enumerate(result[1].items()):
            exercise_standart = [standart for standart in data['exercises']
                                 [exercise[0]] if standart[0] == data['group']][0][1]
            mark = calculate_exercise_mark(exercise[1], exercise_standart)
            marks.append(mark)
            ws.write(10 + i, 2 + j * 2, exercise[1], style_center)
            ws.write(10 + i, 3 + j * 2, mark, style_center)
        total_mark = calculate_total_mark(marks)
        ws.write(10 + i, 8, total_mark, style_center)


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
            'Васильев': {'Упр. №3 Подтягивание': '12', 'Упр. №29 Бег на 60м': '9.0', 'Упр. №27 Бег на 1000м': '4:50', },
            'Иванов': {'Упр. №3 Подтягивание': '32', 'Упр. №29 Бег на 60м': '10.4', 'Упр. №27 Бег на 1000м': '64:30', },
            'Кузнецов': {'Упр. №3 Подтягивание': '22', 'Упр. №29 Бег на 60м': '11.5', 'Упр. №27 Бег на 1000м': '23:10', },
            'Петров': {'Упр. №3 Подтягивание': '12', 'Упр. №29 Бег на 60м': '9.1', 'Упр. №27 Бег на 1000м': '12:30', },
            'Попов': {'Упр. №3 Подтягивание': '1', 'Упр. №29 Бег на 60м': '12.4', 'Упр. №27 Бег на 1000м': '11:40', },
            'Смирнов': {'Упр. №3 Подтягивание': '442', 'Упр. №29 Бег на 60м': '11.7', 'Упр. №27 Бег на 1000м': '12:40', },
            'Соколов': {'Упр. №3 Подтягивание': '2', 'Упр. №29 Бег на 60м': '8.4', 'Упр. №27 Бег на 1000м': '333:40', }
        }
    }
    )
