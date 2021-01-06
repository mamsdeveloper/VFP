import os
import sys

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import *
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooser
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import GridLayout, MDGridLayout
from kivymd.uix.screen import MDScreen
from kivy.properties import ListProperty

import excel_utils
from config_utils import *


#
# Screen managers and Screens
#
class AppScreenManager(ScreenManager):
    def update_settings_students(self, name, students):
        """
        Needed for update list of exps on settings screen
        else app destoes on android
        """
        for exp in self.children[0].classes_exps:
            for item in exp.items_list.children:
                if item.children[1].text == name:
                    item.students = students
                    break

    def update_settings_standards(self, title, standards):
        """
        Needed for update list of exps on settings screen
        else app destoes on android
        """
        exercise, group = title.split(':')
        group = group[1:]

        for exp in self.children[0].exercises_exps:
            if exp.children[1].children[-1].text == exercise:
                for item in exp.items_list.children:
                    if item.children[1].text == group:
                        item.standards = standards
                        break


# Screen that provide default properties for screens
class ParentScreen(MDScreen):
    def redirect(self, instance):
        """
        Create new screen and set it as current
        """
        print('>>> Redirect to', instance.name)
        swipe_direction(self, instance)  # change swipe mod (left or right)

        if instance.name == 'Main':
            if self.name in ('OpenFile', 'SaveFile'):
                self.parent.switch_to(MainScreen(name='Main'))
            else:
                self.open_dialog()

        elif instance.name == 'Settings':
            # when redirect from home page create new settings screen
            if self.name == 'Main':
                self.parent.switch_to(SettingsScreen(name='Settings'))
            # when redirect from settings subpages load exist settings page
            else:
                self.parent.current = 'Settings'

        elif instance.name == 'Create':
            # when redirect from home page create new create screen
            if self.name == 'Main':
                self.parent.switch_to(CreateScreen(name='Create'))
            # when redirect from save screen load exist crate screen
            else:
                self.parent.current = 'Create'

        elif instance.name == 'OpenFile':
            self.parent.switch_to(OpenFileScreen(name='OpenFile'))

        elif instance.name == 'Update':
            # when redirect from open file create new update screen
            if self.name == 'OpenFile':
                path = instance.parent.parent.parent.children[1].children[0].selected
                self.parent.switch_to(UpdateScreen(path, name='Update'))
            # when redirect from save screen load exist update screen
            else:
                self.parent.current = 'Update'

        print('@DONE')

    def open_dialog(self):
        ok_button = MDIconButton(
            icon='arrow-left-circle-outline',
            on_press=self.dialog_callback
        )
        cancel_button = MDIconButton(
            icon='close',
            on_press=self.dialog_callback
        )

        self.dialog = MDDialog(
            title='Вернуться в главное меню?',
            text='Несохраненные данные будут утеряны.',
            size_hint=(.8, None),
            buttons=[ok_button, cancel_button],
            auto_dismiss=False
        )
        self.dialog.open()

    def dialog_callback(self, instance):
        if instance.icon != 'close':
            self.parent.switch_to(MainScreen(name='Main'))
        self.dialog.dismiss()


class MainScreen(ParentScreen):
    pass


class FileChangeScreen():
    def update_values(self):
        if self.name == 'Create':
            self.period = self.settings_area.children[6].text
            teacher_list = self.settings_area.children[4]
        else:
            self.period = self.settings_area.children[2].text
            teacher_list = self.settings_area.children[0]
        self.teacher['name'] = teacher_list.children[2].text
        self.teacher['rank'] = teacher_list.children[1].text
        self.teacher['post'] = teacher_list.children[0].text

    def save_file(self, instance):
        """
        Save screen values to statement
        """
        self.update_values()
        data = {}
        data.update({'school_name': self.school_name})
        data.update({'period': self.period})
        data.update({'teacher': self.teacher})
        data.update({'class_name': self.class_name})
        data.update({'group': self.group})
        data.update({
            'exercises': dict(zip(
                self.exercises.keys(),
                (value for value in self.exercises.values())
            ))
        })

        results = {}
        for student in reversed(self.write_area.children[0].children):
            student_name = student.children[1].text
            student_results = {}
            for standard in reversed(student.children[0].children):
                standard_name = standard.children[1].text
                standard_result = standard.children[0].text
                student_results.update({standard_name: standard_result})
            results.update({student_name: student_results})
        data.update({'results': results})

        # validate
        for key in list(data):
            if not data[key]:
                data.pop(key)

        if len(data) < 7:
            Snackbar('Заполните все поля').show()
        elif len(self.exercises) > 3:
            Snackbar('Не больше 3 упражнений').show()
        else:
            swipe_direction(self, instance)
            self.parent.add_widget(SaveFileScreen(data, name='SaveFile'))
            self.parent.current = 'SaveFile'


class CreateScreen(ParentScreen, FileChangeScreen):
    def __init__(self, **kwargs):
        """
        Init values that will be used for save statement.
        Create areas, set current area
        """
        print('>>> Init Create Screen')
        super().__init__(**kwargs)
        # data
        self.dialog = None
        self.school_name = 'None'
        self.teacher = {
            'name': 'None',
            'rank': 'None',
            'post': 'None'
        }
        self.group = ''
        self.class_name = ''
        self.students = []
        self.exercises = {}
        self.period = ''
        self.settings_area = FileSettingsArea()
        self.write_area = FileWriteArea()
        self.area = 'SettingsArea'
        self.children[0].children[-1].add_widget(self.settings_area)

        try:
            self.apply_config()
        except:
            Snackbar('Что-то не так с настройками').show()
        print('@DONE')

    def change_area(self, instance):
        """
        Change current work area.
        Disable scroll on file settings area
        """
        if self.area != instance.name:
            if instance.name == 'SettingsArea':
                self.open_write_area_dialog()
            else:
                self.children[0].children[-1].clear_widgets()
                self.area = 'WriteArea'
                self.write_area.update_area(
                    self.group, self.class_name, self.students, self.exercises)
                self.children[0].children[-1].do_scroll_y = True
                self.children[0].children[-1].add_widget(self.write_area)
                self.children[0].children[-1].scroll_y = 1

    def update_drop_list(self, drop_list):
        """
        Set new values to class drop list
        """
        for group in drop_list:
            for cls in drop_list[group]:
                self.settings_area.children[0].area.children[0].children[0].add_widget(
                    DropListItem())
                self.settings_area.children[0].area.children[0].children[0].children[0].group = group
                self.settings_area.children[0].area.children[0].children[0].children[0].name = cls[0]
                self.settings_area.children[0].area.children[0].children[0].children[0].students = cls[1]

    def update_checkboxes(self, exercises):
        for exercise in exercises:
            self.settings_area.children[2].children[0].add_widget(
                CB(exercise, exercises[exercise]))

    def update_exercises(self, instance):
        if instance.children[1].active:
            self.exercises.update({instance.text: instance.standards})

            if len(instance.parent.children) == 1:
                instance.parent.parent.spacing = 0
            else:
                instance.parent.parent.spacing = sp(10)

            instance.parent.remove_widget(instance)
            self.settings_area.children[2].children[1].add_widget(instance)
        else:
            self.exercises.pop(instance.text)

            if len(instance.parent.children) == 1:
                instance.parent.parent.spacing = 0
            else:
                instance.parent.parent.spacing = sp(10)

            instance.parent.remove_widget(instance)
            self.settings_area.children[2].children[0].add_widget(instance)

    def apply_config(self):
        """
        Apply app's config to create screen fields
        """
        print('>>> Apply config to Create Screen')
        # get config
        config = get_config()

        # school name
        self.school_name = config['school_name']

        # teacher
        self.teacher = config['teacher']

        teacher_list = self.settings_area.children[4]

        teacher_list.children[2].text = config['teacher']['name']
        teacher_list.children[1].text = config['teacher']['rank']
        teacher_list.children[0].text = config['teacher']['post']

        # exercises checkboxes
        self.update_checkboxes(config['exercises'])

        self.exercises
        # classes list
        drop_list = {}
        for group in config['groups']:
            drop_list.update({group: []})
            for cls in config['groups'][group]:
                drop_list[group].append(cls)

        self.update_drop_list(drop_list)

        for val in locals().values():
            del val

        print('@DONE')

    def open_write_area_dialog(self):
        ok_button = MDIconButton(
            icon='arrow-left-circle-outline',
            on_press=self.write_area_dialog_callback
        )
        cancel_button = MDIconButton(
            icon='close',
            on_press=self.write_area_dialog_callback
        )

        self.dialog = MDDialog(
            title='Перейти к настройкам?',
            text='Введенные данные будут утеряны.',
            size_hint=(.8, None),
            buttons=[ok_button, cancel_button],
            auto_dismiss=False
        )
        self.dialog.open()

    def write_area_dialog_callback(self, instance):
        if instance.icon != 'close':
            self.children[0].children[-1].clear_widgets()
            self.area = 'SettingsArea'
            self.children[0].children[-1].add_widget(self.settings_area)
        self.dialog.dismiss()


class UpdateScreen(ParentScreen, FileChangeScreen):
    def __init__(self, path='', **kwargs):
        """
        Init values that will be used for save statement.
        Create areas, set current area
        """
        print('>>> Init Create Screen')
        super().__init__(**kwargs)
        # data
        self.path = path
        self.dialog = None
        self.school_name = 'None'
        self.teacher = {
            'name': 'None',
            'rank': 'None',
            'post': 'None'
        }
        self.group = ''
        self.class_name = ''
        self.students = []
        self.exercises = {}
        self.period = ''
        self.settings_area = FileSettingsShortenArea()
        self.write_area = FileWriteArea()
        self.area = 'WriteArea'
        self.children[0].children[-1].add_widget(self.write_area)

        try:
            self.load_data()
        except:
            Snackbar('Что-то не так с данными').show()
        print('@DONE')

    def change_area(self, instance):
        """
        Change current work area.
        Disable scroll on file settings area
        """
        if self.area != instance.name:
            if instance.name == 'SettingsArea':
                self.area = 'SettingsArea'
                self.children[0].children[-1].clear_widgets()
                self.children[0].children[-1].add_widget(self.settings_area)
            else:
                self.area = 'WriteArea'
                self.children[0].children[-1].clear_widgets()
                self.children[0].children[-1].add_widget(self.write_area)
                self.children[0].children[-1].do_scroll_y = True
                self.children[0].children[-1].scroll_y = 1

    def load_data(self):
        data = excel_utils.load_file(self.path)
        config = get_config()

        self.school_name = data['school_name']
        self.class_name = data['class_name'].replace(' класс', '')

        for group in config['groups']:
            for class_name in config['groups'][group]:
                if class_name[0] == self.class_name:
                    self.group = group
                    self.students = class_name[1]
                    break
            else:
                break

        self.period = data['period']
        self.settings_area.children[2].text = data['period']

        self.teacher = data['teacher']
        teacher_list = self.settings_area.children[0]
        teacher_list.children[2].text = data['teacher']['name']
        teacher_list.children[1].text = data['teacher']['rank']
        teacher_list.children[0].text = data['teacher']['post']

        for exercise in data['exercises']:
            if exercise in config['exercises'].keys():
                self.exercises.update(
                    {exercise: config['exercises'][exercise]})

        self.write_area.update_area(
            self.group,
            self.class_name,
            self.students,
            self.exercises
        )

        for student, result in zip(
            reversed(self.write_area.children[0].children),
            data['results'].values()
        ):
            for field, exercise in zip(
                reversed(student.children[0].children),
                result.items()
            ):
                field.children[0].text = exercise[1]


class ViewScreen(ParentScreen):
    pass


class SettingsScreen(ParentScreen):
    def __init__(self, **kwargs):
        """
        Create exps' list (needed to predict destoings on android)
        Apply app's config to settings screen values
        """
        print('>>> Init Settings Screen')
        super().__init__(**kwargs)
        self.classes_exps = []
        self.exercises_exps = []
        self.apply_config()
        print('@DONE')

    def update_exps(self, name, exps):
        """
        Update exppanels values by class exps list
        """
        if name == 'classes_exps':
            self.classes_exps = exps.copy()
            self.children[0].children[1].children[0].children[4].clear_widgets()
            for exp in self.classes_exps:
                self.children[0].children[1].children[0].children[4].add_widget(exp)
        else:
            self.exercises_exps = exps.copy()
            self.children[0].children[1].children[0].children[1].clear_widgets()
            for exp in self.exercises_exps:
                self.children[0].children[1].children[0].children[1].add_widget(
                    exp)

    def apply_config(self):
        """
        Apply app's config to settings screen
        """
        print('>>> Apply config to Settings Screen')
        # get config
        config = get_config()

        # screen area widgets
        all_widgets = self.children[0].children[1].children[0]

        # school name
        all_widgets.children[-2].text = config['school_name']

        # teacher
        teacher_list = all_widgets.children[-4]

        teacher_list.children[2].text = config['teacher']['name']
        teacher_list.children[1].text = config['teacher']['rank']
        teacher_list.children[0].text = config['teacher']['post']

        # classes
        exps = []

        for group in config['groups']:
            # create exp panel
            exp = ExpPanel()

            # set group name
            exp.children[1].children[-1].children[1].text = group

            # create items
            for item in config['groups'][group]:
                exp_item = ExpPanelItem()  # create
                exp_item.children[1].children[1].text = item[0]  # set text
                exp_item.students = item[1]  # set students
                exp.items_list.add_widget(exp_item)  # add item to items list

            exps.append(exp)

        self.update_exps('classes_exps', exps)

        # exercises
        exps = []

        for exercise in config['exercises']:
            # create exp panel
            exp = ExpPanel()

            # set group name
            exp.children[1].children[-1].children[1].text = exercise

            # create items
            for item in config['exercises'][exercise]:
                exp_item = ExpPanelItem()  # create
                exp_item.children[1].children[1].text = item[0]  # set text
                exp_item.standards = item[1]  # set standards
                exp.items_list.add_widget(exp_item)  # add item to items list

            exps.append(exp)

        self.update_exps('exercises_exps', exps)

        for val in locals().values():
            del val

        print('@DONE')

    def save_settings(self, instance):
        """
        Save settings from Settings Screen to app's config
        """
        print('>>> Save settings')
        save_config(self)
        Snackbar('Настройки сохранены').show()


class ClassScreen(ParentScreen):
    def __init__(self, students=[], title='', **kwargs):
        """
        Set parent item, students' list and add them to students' box
        """
        super().__init__(**kwargs)
        self.name = kwargs['name']
        self.title = title
        self.students = students
        self.student_box = self.children[0].children[1].children[0].children[1]

        # add only exist students
        for student in self.students:
            self.student_box.add_widget(StudentItem(student))

    def update_students(self):
        """
        Add students from screen items to students' list
        """
        self.students = []
        for item in self.student_box.children:
            # validate
            if item.children[1].children[0].text:
                self.students.append(item.children[1].children[0].text)

        self.students.sort()

    def redirect(self, instance):
        """
        Redefining parent class redirect method to delete screen after redirect
        """
        super().redirect(instance)
        self.parent.remove_widget(self)


class ExerciseScreen(ParentScreen):
    def __init__(self, standards=[], title='', **kwargs):
        """
        Set parent item
        """
        super().__init__(**kwargs)
        self.name = kwargs['name']
        self.title = title
        self.standards = standards

        if len(standards) == 3:
            self.children[0].children[1].children[0].children[4].text = self.standards[0]
            self.children[0].children[1].children[0].children[2].text = self.standards[1]
            self.children[0].children[1].children[0].children[0].text = self.standards[2]

        # Turn off scrolling
        self.children[0].children[1].do_scroll_y = False

    def update_standards(self):
        """
        Add marks standards from screen items to standards' list
        """
        items = self.children[0].children[1].children[0].children
        self.standards = [items[4].text,    # 5
                          items[2].text,    # 4
                          items[0].text]    # 3

    def redirect(self, instance):
        """
        Redefining parent class redirect method to delete screen after redirect
        """
        super().redirect(instance)
        self.parent.remove_widget(self)


class OpenFileScreen(ParentScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_manager = FileManager(
            bg_color=(1, 1, 1, .6),
            sub_color=(.4, .4, .4, .3),
            file_filter=['.xls', '.xlsx']
        )
        self.children[0].children[-1].add_widget(self.file_manager)

    def on_parent(self, *args):
        self.children[0].children[-1].children[-1].update()

    def redirect(self, instance):
        if self.file_manager.selected or instance.name == 'Main':
            super().redirect(instance)
        else:
            Snackbar('Выберите файл').show()


class SaveFileScreen(ParentScreen):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.dialog = None
        self.file_manager = FileManager(
            bg_color=(1, 1, 1, .6),
            sub_color=(.4, .4, .4, .3),
            file_filter=['Hide files']
        )
        self.children[0].children[-1].add_widget(self.file_manager)

    def on_parent(self, *args):
        self.children[0].children[-1].children[-1].update()

    def redirect(self, instance):
        super().redirect(instance)
        self.parent.remove_widget(self)

    def save(self):
        self.open_save_file_dialog()

    def open_save_file_dialog(self):
        ok_button = MDIconButton(
            icon='check',
            on_press=self.save_file_dialog_callback
        )
        ok_button.__setattr__('name', 'Main')
        cancel_button = MDIconButton(
            icon='close',
            on_press=self.save_file_dialog_callback
        )

        self.dialog = MDDialog(
            title='Имя файла',
            type='custom',
            content_cls=SimpleTextInput(hint_text='Имя файла'),
            size_hint=(.8, None),
            buttons=[ok_button, cancel_button],
            auto_dismiss=False
        )
        self.dialog.open()

    def save_file_dialog_callback(self, instance):
        self.dialog.dismiss()
        if instance.icon == 'check':
            is_save = excel_utils.save_file(
                self.data,
                self.file_manager.path,
                self.dialog.content_cls.children[0].text
            )
            
            if is_save:
                Snackbar('Файл сохранен').show()
            else:
                Snackbar('Ошибка сохранения').show()
                
            self.redirect(instance)


def swipe_direction(self, instance):
    """
    Change swipe direction of SM on right or left in relation to touch pos
    """
    if instance.center_x <= self.width/2:
        self.parent.transition.direction = 'right'
    else:
        self.parent.transition.direction = 'left'


#
# Work Areas
#
class ParentArea(GridLayout):
    pass


class MainArea(ParentArea):
    pass


class SettingsArea(ParentArea):
    pass


class ClassArea(ParentArea):
    pass


class ExerciseArea(ParentArea):
    pass


class FileSettingsArea(ParentArea):
    def on_touch_up(self, *args):
        """
        Close drop input on screen touch
        """
        super().on_touch_up(*args)
        if (
            self.children[0].st and
            not self.children[0].area.children[0].collide_point(*args[0].pos) and
            not self.children[0].children[-1].children[0].collide_point(
                *args[0].pos)
        ):
            self.children[0].change_state()


class FileSettingsShortenArea(ParentArea):
    pass


class FileWriteArea(ParentArea):
    def update_area(self, group, class_name, students, exercises):
        """
        Update write area with neew students and exercises
        """
        self.children[1].text = f'Результаты {class_name} класса:'

        for student in students:
            self.children[0].add_widget(WriteAreaItem())
            self.children[0].children[0].children[1].text = student
            for exercise in exercises:
                if not exercises[exercise]:
                    continue

                if any([i[0] == group for i in exercises[exercise]]):
                    self.children[0].children[0].children[0].add_widget(
                        ExerciseResultItem())
                    self.children[0].children[0].children[0].children[0].children[1].text = exercise

        l = len(self.children[0].children) - len(students)
        if l:
            self.children[0].clear_widgets(self.children[0].children[-l:])


#
# Expansion Panel
#
class ExpsList(MDGridLayout):
    def add_exp(self, instance):
        """
        Add new exp panel to exps list.
        Update screen's exps list
        Close opened exps.
        """
        self.add_widget(ExpPanel(
            placeholder='Курс (класс)' if self.name == 'classes_exps' else 'Упражнение'
        ))

        self.close_all()
        self.update_exps()

    def del_exp(self, instance):
        """
        Del exp from list
        Update screen's exps list
        """
        self.remove_widget(instance.parent.parent)
        self.update_exps()

    def close_all(self):
        for exp in self.children:
            if exp.st:
                exp.change_state()

    def update_exps(self):
        exps = []
        for exp in reversed(self.children):
            exps.append(exp)
        self.parent.parent.parent.parent.update_exps(self.name, exps)


class ExpPanel(MDGridLayout):
    def __init__(self, placeholder=''):
        """
        Init panel's main widgets.
        Creare items list.
        Change stete to close
        """
        super().__init__()
        # init box and right button
        self.add_widget(ExpPanelBox())
        self.add_widget(ExpRightButton())

        # init items list
        self.items_list = ExpPanelItemsList()

        # add first item, items list and add-button in box
        self.placeholder = placeholder
        self.children[1].add_widget(ExpPanelFirstItem(self.placeholder))
        self.children[1].add_widget(self.items_list)
        self.children[1].add_widget(ExpPanelAddButton())

        self.children[1].children[1].size_hint_y = 0
        self.children[1].children[1].opacity = 0
        self.children[1].children[0].height = 0
        self.children[1].children[0].opacity = 0
        # self close/open state
        self.st = False

    def change_state(self):
        """
        Change state of panel (close or open)
        """
        # close
        if self.st:
            self.children[1].children[1].size_hint_y = 0
            self.children[1].children[1].opacity = 0
            self.children[1].children[0].height = 0
            self.children[1].children[0].opacity = 0

            self.children[1].children[2].children[0].icon = 'menu-right'
        # open
        else:
            self.parent.close_all()
            self.children[1].children[1].size_hint_y = None
            self.children[1].children[1].height = self.children[1].children[1].minimum_height
            self.children[1].children[1].opacity = 1
            self.children[1].children[0].height = sp(40)
            self.children[1].children[0].opacity = 1

            self.children[1].children[2].children[0].icon = 'arrow-down-drop-circle'

        self.st = not self.st


class ExpPanelBox(MDGridLayout):
    pass


class ExpPanelItemsList(MDGridLayout):
    def add_item(self):
        """
        Add new item to exp items list
        """
        self.add_widget(ExpPanelItem())

    def del_item(self, instance):
        """
        del item from list
        """
        self.remove_widget(instance)


class ExpRightButton(AnchorLayout):
    pass


class ExpPanelFirstItem(GridLayout):
    def __init__(self, placeholder):
        """
        docstring
        """
        super().__init__()
        self.placeholder = placeholder


class ExpPanelAddButton(AnchorLayout):
    pass


class ExpPanelItem(GridLayout):
    def update(self, instance):
        if instance.parent.parent.parent.parent.parent.parent.name == 'classes_exps':
            self.update_class(instance)
        else:
            self.update_exercises(instance)

    def update_class(self, instance):
        """
        Create class update screen, redirect to it.
        """
        # create class screen
        self.class_scr = ClassScreen(
            self.students, instance.text, name=instance.text)
        # add screen in screen manager
        sm = self.parent.parent.parent.parent.parent.parent.parent.parent.parent
        sm.transition.direction = 'left'
        sm.add_widget(self.class_scr)
        sm.current = instance.text

        del sm

    def update_exercises(self, instance):
        """
        Create exercises screen, redirect to it.
        """
        # create class screen
        title = self.parent.parent.children[-1].text + ': ' + instance.text
        self.exercise_scr = ExerciseScreen(
            self.standards, title, name=instance.text)

        # add screen in screen manager
        sm = self.parent.parent.parent.parent.parent.parent.parent.parent.parent
        sm.transition.direction = 'left'
        sm.add_widget(self.exercise_scr)
        sm.current = instance.text

        del sm


#
# Drop Input
#
class DropInput(MDGridLayout):
    def __init__(self, **kwargs):
        """
        Init drop input area, set drop input state to close
        """
        super().__init__(**kwargs)
        self.area = DropInputDropArea()
        self.add_widget(DropInputFirstItem())
        self.add_widget(self.area)
        self.area.children[0].height = 0
        self.st = False

    def change_state(self):
        """
        Change drop input state (close or open)
        """
        self.parent.parent.scroll_to(self)
        if self.st:
            self.area.opacity = 0
            self.area.children[0].height = 0
            self.children[-1].children[0].icon = 'menu-right'
            self.get_root_window(
            ).children[-1].current_screen.children[0].children[-1].do_scroll_y = True
        else:
            self.area.opacity = 1
            self.area.children[0].height = sp(176)
            self.children[-1].children[0].icon = 'arrow-down-drop-circle'
            self.get_root_window(
            ).children[-1].current_screen.children[0].children[-1].do_scroll_y = False

        self.st = not self.st

    def choose_item(self, instance):
        """
        Choose item frop drop list and set to label, set students list to screen
        """
        self.children[-1].children[-1].text = instance.name
        self.parent.parent.parent.parent.group = instance.group
        self.parent.parent.parent.parent.class_name = instance.name
        self.parent.parent.parent.parent.students = instance.students
        self.change_state()


class DropInputDropArea(AnchorLayout):
    pass


class DropInputScroll(ScrollView):
    pass


class DropInputFirstItem(GridLayout):
    pass


class DropListItem(Button):
    def on_touch_down(self, *args):
        """
        Choose item
        """
        super().on_touch_down(*args)
        # to exclude touching of other items
        if self.collide_point(*args[0].pos):
            self.parent.parent.parent.parent.choose_item(self)


#
# Area's items
#
class TunedTextInput(TextInput):
    def adopt_scroll(self):
        area_h = self.get_root_window(
        ).children[-1].current_screen.children[0].children[-1].children[0].height
        scroll_h = self.get_root_window(
        ).children[-1].current_screen.children[0].children[-1].height

        if self.focus and area_h > scroll_h:
            self.get_root_window(
            ).children[-1].current_screen.children[0].children[-1].scroll_to(self)


class SimpleTextInput(FloatLayout):
    pass


class StudentsList(MDGridLayout):
    def add_student(self):
        """
        Add student to student list
        """
        self.add_widget(StudentItem())

    def del_student(self, instance):
        """
        Del student from list
        """
        self.remove_widget(instance)


class StudentItem(GridLayout):
    def __init__(self, text='', **kwargs):
        """
        Set self text from arguments
        """
        super().__init__(**kwargs)
        self.text = text


class CB(MDGridLayout):
    def __init__(self, text, standards):
        super().__init__()
        self.st = True
        self.text = text
        self.standards = standards

    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y) and not self.children[1].collide_point(touch.x, touch.y):
            if self.children[1].active:
                if self.st:
                    self.st = False
                else:
                    self.children[1].active = False
                    self.st = True
            else:
                self.children[1].active = True
                self.st = True
        else:
            super().on_touch_up(touch)


class ExerciseResultItem(MDGridLayout):
    pass


class WriteAreaItem(MDGridLayout):
    pass


class Snackbar(MDFloatLayout):
    def __init__(self, text, **kwargs):
        super().__init__()
        self.text = text
        self.duration = 3.5
        self._interval = 2

    def show(self):
        """Show the snackbar."""

        def wait_interval(interval):
            self._interval += interval
            if self._interval > self.duration:
                anim = Animation(y=-self.ids.box.height, d=0.2)
                anim.bind(
                    on_complete=lambda *args: Window.parent.remove_widget(self)
                )
                anim.start(self.ids.box)
                Clock.unschedule(wait_interval)
                self._interval = 0

        Window.parent.add_widget(self)
        anim = Animation(y=sp(15), d=0.2)
        anim.bind(
            on_complete=lambda *args: Clock.schedule_interval(wait_interval, 0)
        )
        anim.start(self.ids.box)


class FileManager(MDGridLayout):
    def __init__(self, path=None, bg_color=(1, 1, 1, 1), sub_color=(0, 0, 0, 1), file_filter=[]):
        super().__init__()
        self.bg_color = bg_color
        self.sub_color = sub_color
        if sys.platform == 'linux':
            self.path = '/storage/emulated/0/'
        else:
            self.path = 'C:/Coding/VFP/programm/'
        self.file_filter = file_filter
        self.selected = ''

    def update(self, *args):
        try:
            self.width = self.get_root_window().width
        except AttributeError:
            pass

        self.update_widgets()

    def update_widgets(self):
        self.children[0].children[0].clear_widgets()
        try:
            list_dir = os.listdir(self.path)
            items_list = []
            for file in list_dir:
                if os.path.isdir(self.path + file):
                    items_list.append((file, 'dir'))
                else:
                    if self.file_filter:
                        p, e = os.path.splitext(file)
                        if e in self.file_filter:
                            items_list.append((file, 'file'))
                    else:
                        items_list.append((file, 'file'))
            items_list.sort(key=lambda x: x[1] == 'file')
            for item in items_list:
                self.children[0].children[0].add_widget(
                    FileManagerItem(self.width * .18, item[0], item[1]))
        except PermissionError:
            pass

        if self.children[0].children[0].children:
            self.children[0].scroll_y = 1

    def turn_back(self):
        try:
            if len(self.path.split('/')) > 2 and self.path != '/storage/emulated/0/':
                self.path = '/'.join(self.path.split('/')[:-2]) + '/'
                self.selected = ''
                self.update_widgets()
        except PermissionError:
            pass

    def select(self, instance):
        if instance.tp == 'file':
            self.selected = self.path + instance.name
            for item in self.children[0].children[0].children:
                if self.path + item.name == self.selected:
                    item.children[1].st = True
                else:
                    item.children[1].st = False
        else:
            self.path = self.path + instance.name + '/'
            self.selected = ''
            self.update_widgets()


class FileManagerItem(MDGridLayout):
    def __init__(self, font_size, name, tp):
        super().__init__()
        self.name = name
        self.tp = tp
        if self.tp == 'dir':
            self.icon = 'folder-outline'
        else:
            if [e for e in ('.xls', 'xlsx') if e in self.name]:
                self.icon = 'file-table-outline'
            else:
                self.icon = 'file-document-outline'

        self.font_size = font_size

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.parent.parent.select(self)

#
# Application
#
class App(MDApp):
    def build(self):
        """
        Set app's values: title, icon, theme.
        Create and return ScreenManager
        """
        Builder.load_file('VFP.kv')
        self.theme_cls.primary_palette = 'Gray'
        sm = AppScreenManager()
        sm.add_widget(MainScreen(name='Main'))
        sm.current = 'Main'

        return sm


# Running application
def main():
    Clock.max_iteration = 1000
    Window.softinput_mode = 'below_target'
    app = App()
    app.run()


if __name__ == '__main__':
    main()
