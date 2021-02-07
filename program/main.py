"""
variable "widget" use to replase
huge syntax constructions for accessing widgets.
"""


import os
import sys

from kivy.utils import platform
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import sp
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
    """Main app widget.Contain methods needful for screens connection."""

    def update_settings_students(self, name, students):
        """
        Needed for update list of exps on settings screen
        else app crashes on android.
        """
        for exp in self.children[0].classes_exps:
            for item in exp.items_list.children:
                if item.children[1].text == name:
                    item.students = students
                    break

    def update_settings_standards(self, title, standards):
        """
        Needed for update list of exps on settings screen
        else app crashes on android.
        """
        exercise, group = title.split(':')
        group = group[1:]

        for exp in self.children[0].exercises_exps:
            if exp.children[1].children[-1].text == exercise:
                for item in exp.items_list.children:
                    if item.children[1].text == group:
                        item.standards = standards
                        break

    def on_kv_post(self, *args):
        """To ask storage permissions on firs start."""
        if platform == 'win':
            return
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])


# Screen that provide default properties for screens
class ParentScreen(MDScreen):
    """Basic class with common methods for all screens."""

    def redirect(self, instance):
        """Create new screen and set it as current."""
        print('>>> Redirect to', instance.name)
        swipe_direction(self, instance)  # change swipe mod (left or right)

        if instance.name == 'Main':
            # if some needful data in current screen ask to redirect else no
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
                path = instance.parent.parent.parent \
                    .children[1].children[0].selected
                self.parent.switch_to(UpdateScreen(path, name='Update'))
            # when redirect from save screen load exist update screen
            else:
                self.parent.current = 'Update'

        print('@DONE')

    def open_dialog(self):
        """
        Open dialog when redirect from screens
        with some data to main screen.
        to ask confirmation for redirect.
        """
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
        """Redirect to main screen if user confirm it."""
        if instance.icon != 'close':
            self.parent.switch_to(MainScreen(name='Main'))
        self.dialog.dismiss()


class MainScreen(ParentScreen):
    """
    Screen with redirect buttons to create,
    open file and settings screens.
    """
    pass


class FileChangeScreen():
    """Base class for Create and Update screens."""

    def __init__(self, **kwargs):
        self.dialog = None
        # settings
        self.settings = {
            'school_name': '',
            'teacher': {
                'name': '',
                'rank': '',
                'post': ''
            },
            'group': '',
            'class_name': '',
            'students': [],
            'exercises': {},
            'period': '',
        }

    def update_values(self):
        """Save values from text inputs."""
        # different items pos on different screens
        i = -4 if self.name == 'Update' else 0
        self.settings['period'] = self.settings_area.children[i+6].text
        teacher_list = self.settings_area.children[i+4]
        self.settings['teacher']['name'] = teacher_list.children[2].text
        self.settings['teacher']['rank'] = teacher_list.children[1].text
        self.settings['teacher']['post'] = teacher_list.children[0].text

    def save_file(self, instance):
        """Forming and validate data, create statement xls file."""
        self.update_values()
        data = self.settings.copy()

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

        if len(data) < 8:
            Snackbar('Заполните все поля').show()
        elif len(self.settings['exercises']) > 3:
            Snackbar('Не больше 3 упражнений').show()
        else:
            swipe_direction(self, instance)
            self.parent.add_widget(SaveFileScreen(data, name='SaveFile'))
            self.parent.current = 'SaveFile'


class CreateScreen(ParentScreen, FileChangeScreen):
    """ Screen for create new excel file."""

    def __init__(self, **kwargs):
        """
        Init values that will be used for save statement.
        Create areas, set current area.
        """
        print('>>> Init Create Screen')
        super().__init__(**kwargs)
        # need to check settings change that can influence on write area
        self.last_settings = {
            'group': '',
            'class_name': '',
            'students': [],
            'exercises': {},
        }

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
        Disable scroll on file settings area.
        """
        if self.area != instance.name:
            if instance.name == 'SettingsArea':
                self.open_write_area_dialog()
            else:
                self.area = 'WriteArea'
                self.children[0].children[-1].clear_widgets()
                # if settings that can influence on write area
                # is changed update write area else no
                inf_setting = {}  # settings that can change write area
                for key in ('group', 'class_name', 'students', 'exercises'):
                    inf_setting.update({key: self.settings[key]})

                if self.last_settings != inf_setting:
                    self.write_area.update_area(
                        self.settings['group'],
                        self.settings['class_name'],
                        self.settings['students'],
                        self.settings['exercises']
                    )
                self.children[0].children[-1].do_scroll_y = True
                self.children[0].children[-1].add_widget(self.write_area)
                self.children[0].children[-1].scroll_y = 1

                # update last settings by new values
                for key, value in inf_setting.items():
                    # copy values that create link on assignment
                    if type(value) in (list, dict):
                        self.last_settings.update({key: value.copy()})
                    else:
                        self.last_settings.update({key: value})

    def create_drop_list(self, groups):
        """Set new values to class drop list."""
        for group in groups:
            for cls in groups[group]:
                widget = self.settings_area.children[0] \
                    .area.children[0].children[0]
                widget.add_widget(DropListItem())
                widget.children[0].group = group
                widget.children[0].name = cls[0]
                widget.children[0].students = cls[1]

    def create_checkboxes(self, exercises):
        """Create checkboxes by config data."""
        for exercise in exercises:
            self.settings_area.children[2].children[0].add_widget(
                CB(exercise, exercises[exercise]))

    def update_checkboxes(self, instance):
        """
        Update activated/disactivate checkboxes lists 
        when press on CB press.
        """
        if instance.children[1].active:
            self.settings['exercises'].update(
                {instance.text: instance.standards})
        else:
            self.settings['exercises'].pop(instance.text)

        if len(instance.parent.children) == 1:
            instance.parent.parent.spacing = 0
        else:
            instance.parent.parent.spacing = sp(10)
        instance.parent.remove_widget(instance)
        # if is active add to 1-list else to 0-list
        self.settings_area.children[2].children[(
            instance.children[1].active)*1].add_widget(instance)

    def apply_config(self):
        """Apply app's config to create screen fields."""
        print('>>> Apply config to Create Screen')
        # get config
        config = get_config()

        # school name
        self.settings['school_name'] = config['school_name']

        # teacher
        self.settings['teacher'] = config['teacher']

        teacher_list = self.settings_area.children[4]
        teacher_list.children[2].text = config['teacher']['name']
        teacher_list.children[1].text = config['teacher']['rank']
        teacher_list.children[0].text = config['teacher']['post']

        # exercises checkboxes
        self.create_checkboxes(config['exercises'])

        # classes list
        self.create_drop_list(config['groups'])
        print('@DONE')

    def open_write_area_dialog(self):
        """
        Show dialog when redirect from write area 
        to tell that data can be lost.
        """
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
            text='Введенные данные могут быть утеряны.',
            size_hint=(.8, None),
            buttons=[ok_button, cancel_button],
            auto_dismiss=False
        )
        self.dialog.open()

    def write_area_dialog_callback(self, instance):
        """Change area if user comfirm it."""
        if instance.icon != 'close':
            self.children[0].children[-1].clear_widgets()
            self.area = 'SettingsArea'
            self.children[0].children[-1].add_widget(self.settings_area)
        self.dialog.dismiss()


class UpdateScreen(ParentScreen, FileChangeScreen):
    """ Screen for change values in opened file."""

    def __init__(self, path='', **kwargs):
        """
        Init values that will be used for save statement.
        Create areas, set current area.
        """
        print('>>> Init Create Screen')
        super().__init__(**kwargs)
        self.path = path

        self.settings_area = FileSettingsShortenArea()
        self.write_area = FileWriteArea()
        self.area = 'WriteArea'

        try:
            self.load_data()
        except:
            Snackbar('Что-то не так с данными').show()
        print('@DONE')

    def change_area(self, instance):
        """
        Change current work area.
        Disable scroll on file settings area.
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
        """Load data from excel file and apply it to fields and variables."""
        data = excel_utils.load_file(self.path)
        config = get_config()

        self.settings['school_name'] = data['school_name']
        self.settings['class_name'] = data['class_name'].replace(' класс', '')

        for group in config['groups']:
            for class_name in config['groups'][group]:
                if class_name[0] == self.settings['class_name']:
                    self.settings['group'] = group
                    self.settings['students'] = class_name[1]
                    break
            else:
                break

        self.settings['period'] = data['period']
        self.settings_area.children[2].text = data['period']

        self.settings['teacher'] = data['teacher']
        teacher_list = self.settings_area.children[0]
        teacher_list.children[2].text = data['teacher']['name']
        teacher_list.children[1].text = data['teacher']['rank']
        teacher_list.children[0].text = data['teacher']['post']

        for exercise in data['exercises']:
            if exercise in config['exercises'].keys():
                self.settings['exercises'].update(
                    {exercise: config['exercises'][exercise]})

        self.write_area.update_area(
            self.settings['group'],
            self.settings['class_name'],
            self.settings['students'],
            self.settings['exercises']
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


class SettingsScreen(ParentScreen):
    """
    Screen with app settings such as:
    -School name
    -Teacher rank, name and post
    -Groups, classes and students
    -Exercises and standards
    """

    def __init__(self, **kwargs):
        """
        Create exps' list (needed to predict crashes on android).
        Apply app's config to settings screen values.
        """
        print('>>> Init Settings Screen')
        super().__init__(**kwargs)
        self.classes_exps = []
        self.exercises_exps = []
        self.apply_config()
        print('@DONE')

    def create_exps(self, exps_type, iter_dict):
        """Create expansion panels."""
        exps = []

        for item in iter_dict:
            # create exp panel
            exp = ExpPanel()

            # set group if type - classes or exercise if exercises
            exp.children[1].children[-1].children[1].text = item

            # create items
            for item in iter_dict[item]:
                exp_item = ExpPanelItem()  # create
                exp_item.children[1].children[1].text = item[0]  # set text
                if exps_type == 'classes_exps':
                    exp_item.students = item[1]  # set students
                else:
                    exp_item.standards = item[1]  # set standards
                exp.items_list.add_widget(exp_item)  # add item to items list

            exps.append(exp)
        self.update_exps(exps_type, exps)

    def update_exps(self, name, exps):
        """Update exppanels values by class exps list"""
        widget = self.children[0].children[1].children[0]
        if name == 'classes_exps':
            self.classes_exps = exps.copy()
            widget.children[4].clear_widgets()
            for exp in self.classes_exps:
                widget.children[4].add_widget(
                    exp)
        else:
            self.exercises_exps = exps.copy()
            widget.children[1].clear_widgets()
            for exp in self.exercises_exps:
                widget.children[1].add_widget(exp)

    def apply_config(self):
        """Apply app's config to settings screen."""
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
        self.create_exps('classes_exps', config['groups'])
        # exercises
        self.create_exps('exercises_exps', config['exercises'])

        print('@DONE')

    def save_settings(self, instance):
        """Save settings from Settings Screen to app's config."""
        print('>>> Save settings')
        save_config(self)
        Snackbar('Настройки сохранены').show()


class SubScreen():
    """Screens that deletes after redirect"""

    def redirect(self, instance):
        """
        Redefining parent class redirect method 
        to delete screen after redirect.
        """
        super().redirect(instance)
        self.parent.remove_widget(self)


class ClassScreen(ParentScreen, SubScreen):
    """Screen for add and del students from some class in settings screen."""

    def __init__(self, students=[], title='', **kwargs):
        """Set parent item, students' list and add them to students' box."""
        super().__init__(**kwargs)
        self.name = kwargs['name']
        self.title = title
        self.students = students
        self.student_box = self.children[0].children[1] \
            .children[0].children[1]
        for student in self.students:
            self.student_box.add_widget(StudentItem(student))

    def update_students(self):
        """Add students from screen items to students' list."""
        self.students = []
        for item in self.student_box.children:
            if item.children[1].children[0].text:  # if not empty
                self.students.append(item.children[1].children[0].text)
        self.students.sort()


class ExerciseScreen(ParentScreen, SubScreen):
    """Screen for set exercise standards."""

    def __init__(self, standards=[], title='', **kwargs):
        """Set parent item."""
        super().__init__(**kwargs)
        self.name = kwargs['name']
        self.title = title
        self.standards = standards
        # set data to  fields
        for i, standard in enumerate(reversed(self.standards)):
            self.children[0].children[1].children[0] \
                .children[i * 2].text = standard
        # Turn off scrolling
        self.children[0].children[1].do_scroll_y = False

    def update_standards(self):
        """Add marks standards from screen items to standards' list."""
        items = self.children[0].children[1].children[0].children
        self.standards = [
            items[4].text,    # 5
            items[2].text,    # 4
            items[0].text     # 3
        ]


class FileManagerScreen():
    """Basic screen for screens that use screen manager."""

    def on_parent(self, *args):
        """
        When screen is already load need to update file manager width,
        because default it incorrect
        """
        self.children[0].children[-1].children[-1].update()


class OpenFileScreen(ParentScreen, FileManagerScreen):
    """Screen with file chooser."""

    def __init__(self, **kwargs):
        """Create file manager that show folders and excel files."""
        super().__init__(**kwargs)
        self.file_manager = FileManager(
            bg_color=(1, 1, 1, .6),
            sub_color=(.4, .4, .4, .3),
            file_filter=['.xls', '.xlsx']
        )
        self.children[0].children[-1].add_widget(self.file_manager)

    def redirect(self, instance):
        """
        Redefining parent class redirect method to 
        validate file selection
        """
        if self.file_manager.selected or instance.name == 'Main':
            super().redirect(instance)
        else:
            Snackbar('Выберите файл').show()


class SaveFileScreen(ParentScreen, FileManagerScreen, SubScreen):
    """Screen with file chooser and save dialog."""

    def __init__(self, data, **kwargs):
        """Create file manager that show only folders"""
        super().__init__(**kwargs)
        self.data = data
        self.dialog = None
        self.file_manager = FileManager(
            bg_color=(1, 1, 1, .6),
            sub_color=(.4, .4, .4, .3),
            # All files will hide, because this extension doesn't exist
            file_filter=['Hide files']
        )
        self.children[0].children[-1].add_widget(self.file_manager)

    def save(self):
        """Open save dialog."""
        self.open_save_file_dialog()

    def open_save_file_dialog(self):
        """Create dialog with file name input."""
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
        """
        Save file if user confirm it, check save errors, redirect after save
        """
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
    """Basic class for all areas with common KV lang properties"""
    pass


class MainArea(ParentArea):
    """Work area of Main Screen. Contains KV lang properties"""
    pass


class SettingsArea(ParentArea):
    """Work area of Settings Screen. Contains KV lang properties"""
    pass


class ClassArea(ParentArea):
    """Work area of Class Screen. Contains KV lang properties"""
    pass


class ExerciseArea(ParentArea):
    """Work area of Exercise Screen. Contains KV lang properties"""
    pass


class FileSettingsArea(ParentArea):
    """
    Work area of Create Screen with file settings. 
    Contains KV lang properties and touch_up method.
    """

    def on_touch_up(self, *args):
        """Close drop input on screen touch."""
        super().on_touch_up(*args)
        if (
            self.children[0].st
            and
            not self.children[0].area.children[0].collide_point(*args[0].pos)
            and
            not self.children[0].children[-1].children[0].collide_point(
                *args[0].pos)
        ):
            self.children[0].change_state()


class FileSettingsShortenArea(ParentArea):
    """
    Work area of Create Screen with some file settings. 
    Contains KV lang properties.
    """
    pass


class FileWriteArea(ParentArea):
    """
    Work area of Create Screen with classes marks inputs. 
    Contains KV lang properties.
    """

    def update_area(self, group, class_name, students, exercises):
        """Update write area with new students and exercises."""
        self.children[1].text = f'Результаты {class_name} класса:'

        for student in students:
            self.children[0].add_widget(WriteAreaItem())
            # set student name to write area
            self.children[0].children[0].children[1].text = student
            for exercise in exercises:
                # if exercise standarts is empty
                if not exercises[exercise]:
                    continue

                # if exercise standarts for current group exist
                if any([i[0] == group for i in exercises[exercise]]):
                    self.children[0].children[0].children[0].add_widget(
                        ExerciseResultItem())
                    self.children[0].children[0].children[0] \
                        .children[0].children[1].text = exercise

        # this need to clear last widgets after new is added
        # because if it does before program crash with
        # "weakly-object doesn't exist" error
        l = len(self.children[0].children) - len(students)
        if l:
            self.children[0].clear_widgets(self.children[0].children[-l:])


#
# Expansion Panel
#
class ExpsList(MDGridLayout):
    """Widget that contain Expansion Panels."""

    def add_exp(self, instance):
        """
        Add new exp panel to exps list.
        Update screen's exps list.
        Close opened exps.
        """
        ph = 'Курс (класс)' if self.name == 'classes_exps' else 'Упражнение'
        self.add_widget(ExpPanel(placeholder=ph))

        self.close_all()
        self.update_exps()

    def del_exp(self, instance):
        """Del exp from list. Update screen's exps list."""
        self.remove_widget(instance.parent.parent)
        self.update_exps()

    def close_all(self):
        """Close opened exps."""
        for exp in self.children:
            if exp.st:
                exp.change_state()

    def update_exps(self):
        """Create list of exps and call screen update method."""
        exps = []
        for exp in reversed(self.children):
            exps.append(exp)
        self.parent.parent.parent.parent.update_exps(self.name, exps)


class ExpPanel(MDGridLayout):
    """
    Panel with opened/closed area.
    Consist always-viewed widget and widget that can hide.
    """

    def __init__(self, placeholder=''):
        """
        Init panel's main widgets. 
        Create items list. Change state to close.
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
        # hide closed/opened area
        self.children[1].children[1].size_hint_y = 0
        self.children[1].children[1].opacity = 0
        self.children[1].children[0].height = 0
        self.children[1].children[0].opacity = 0
        # self is closed/opened state
        self.st = False

    def change_state(self):
        """Change state of panel (close or open)"""
        # close
        if self.st:
            self.children[1].children[1].size_hint_y = 0
            self.children[1].children[1].opacity = 0
            self.children[1].children[0].height = 0
            self.children[1].children[0].opacity = 0

            self.children[1].children[2].children[0].icon = 'menu-right'
        # open
        else:
            widget = self.children[1]
            self.parent.close_all()
            widget.children[1].size_hint_y = None
            widget.children[1].height = widget.children[1].minimum_height
            widget.children[1].opacity = 1
            widget.children[0].height = sp(40)
            widget.children[0].opacity = 1

            widget.children[2].children[0].icon = 'arrow-down-drop-circle'

        self.st = not self.st


class ExpPanelFirstItem(GridLayout):
    """
    Always-viewed exp widget. 
    Consist text input and close/open button.
    """

    def __init__(self, placeholder):
        """Set placeholder variable for text input"""
        super().__init__()
        self.placeholder = placeholder


class ExpRightButton(AnchorLayout):
    """Button for delete exp panel."""
    pass


class ExpPanelBox(MDGridLayout):
    """Closed/Opened exp widget."""
    pass


class ExpPanelItemsList(MDGridLayout):
    """Widget that contains typical exp widgets."""

    def add_item(self):
        """Add new item to exp items list."""
        self.add_widget(ExpPanelItem())

    def del_item(self, instance):
        """Del item from list."""
        self.remove_widget(instance)


class ExpPanelItem(GridLayout):
    """
    Exp panel typical widget. 
    Consist text input, write button and item delete button.
    """

    def update(self, instance):
        """Create sub screen to change item values."""
        if instance.parent.parent.parent.parent. \
                parent.parent.name == 'classes_exps':
            self.update_class(instance)
        else:
            self.update_exercises(instance)

    def update_class(self, instance):
        """Create and open class update screen."""
        # create class screen
        self.class_scr = ClassScreen(
            self.students, instance.text, name=instance.text)
        # add screen in screen manager
        sm = self.get_root_window().children[-1]
        sm.transition.direction = 'left'
        sm.add_widget(self.class_scr)
        sm.current = instance.text

    def update_exercises(self, instance):
        """Create and open exercises screen."""
        # create class screen
        title = self.parent.parent.children[-1].text + ': ' + instance.text
        self.exercise_scr = ExerciseScreen(
            self.standards, title, name=instance.text)

        # add screen in screen manager
        sm = self.get_root_window().children[-1]
        sm.transition.direction = 'left'
        sm.add_widget(self.exercise_scr)
        sm.current = instance.text


class ExpPanelAddButton(AnchorLayout):
    """Button for add exp list item."""
    pass


#
# Drop Input
#
class DropInput(MDGridLayout):
    """Input with drop-down menu."""

    def __init__(self, **kwargs):
        """Init drop-down area, set drop input state to close"""
        super().__init__(**kwargs)
        self.area = DropInputDropArea()
        self.add_widget(DropInputFirstItem())
        self.add_widget(self.area)
        self.area.children[0].height = 0
        self.st = False

    def change_state(self):
        """Change drop input state (close or open)."""
        self.parent.parent.scroll_to(self)
        # close
        if self.st:
            self.area.opacity = 0
            self.area.children[0].height = 0
            self.children[-1].children[0].icon = 'menu-right'
            self.parent.parent.do_scroll_y = True
        # open
        else:
            self.area.opacity = 1
            self.area.children[0].height = sp(176)
            self.children[-1].children[0].icon = 'arrow-down-drop-circle'
            self.parent.parent.do_scroll_y = False

        self.st = not self.st

    def choose_item(self, instance):
        """
        Choose item from drop list and set to label, 
        set students list to screen
        """
        self.children[-1].children[-1].text = instance.name
        screen = self.parent.parent.parent.parent
        screen.settings['group'] = instance.group
        screen.settings['class_name'] = instance.name
        screen.settings['students'] = instance.students
        self.change_state()


class DropInputFirstItem(GridLayout):
    """Text field that view selected item."""
    pass


class DropInputDropArea(AnchorLayout):
    """Drop-down widget."""
    pass


class DropInputScroll(ScrollView):
    """Scroll area of drop-down widget."""
    pass


class DropListItem(Button):
    """Item of drop-down menu."""

    def on_touch_down(self, *args):
        """ Choose item."""
        # to exclude touching of other items
        if self.collide_point(*args[0].pos):
            self.parent.parent.parent.parent.choose_item(self)


#
# Area's items
#
class TunedTextInput(TextInput):
    """Text input with KV lang properties. Used in all inputs."""

    def adopt_scroll(self):
        """
        Need for work areas with aren't full filled scroll area 
        that scrolls incorrect.
        """
        widget = self.get_root_window().children[-1] \
            .current_screen.children[0].children[-1]
        area_h = widget.children[0].height
        scroll_h = widget.height
        # only if scroll area is full filled
        if self.focus and area_h > scroll_h:
            widget.scroll_to(self)


class SimpleTextInput(FloatLayout):
    """Simple text input used in many widgets."""
    pass


class StudentsList(MDGridLayout):
    """List of students widgets on Class Screen."""

    def add_student(self):
        """Add student to student list."""
        self.add_widget(StudentItem())

    def del_student(self, instance):
        """Del student from list."""
        self.remove_widget(instance)


class StudentItem(GridLayout):
    """Item of students list."""

    def __init__(self, text=''):
        """Set self text from arguments."""
        super().__init__()
        self.text = text


class CB(MDGridLayout):
    """CheckBox with exercise name."""

    def __init__(self, text, standards):
        """Set exercise name and standarts, ch state."""
        super().__init__()
        self.st = True
        self.text = text
        self.standards = standards

    def on_touch_up(self, touch):
        """Check touch on label."""
        # if click on label
        if (
            self.collide_point(touch.x, touch.y)
            and
            not self.children[1].collide_point(touch.x, touch.y)
        ):
            # that need to copminsate MDCheckBox methods
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


class WriteAreaItem(MDGridLayout):
    """
    Item of Write Area students list.
    Consist student name and results inputs.
    """
    pass


class ExerciseResultItem(MDGridLayout):
    """
    Student result input on write area.
    Consist exercise name and text input.
    """
    pass


class Snackbar(MDFloatLayout):
    """Pop-up tip. Based on MDSnackbar methods with fixed bugs"""

    def __init__(self, text, **kwargs):
        """Set open/close and showwen time."""
        super().__init__()
        self.text = text
        # it works strange because taken from mdsnackbar that has some bugs
        # the simple way is takes different values
        # to set open and showwen time
        self.duration = 3.5
        self._interval = 2

    def show(self):
        """Show the snackbar. MDSnackBar fixed method"""

        def wait_interval(interval):
            self._interval += interval
            if self._interval > self.duration:
                anim = Animation(y=-self.ids.box.height, d=0.2)
                anim.bind(on_complete=lambda *args:
                          Window.parent.remove_widget(self))
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
    """File manager widget."""

    def __init__(
        self,
        path=None,
        bg_color=(1, 1, 1, 1),
        sub_color=(0, 0, 0, 1),
        file_filter=[]
    ):
        """Set color, path and file filter."""
        super().__init__()
        self.bg_color = bg_color
        self.sub_color = sub_color
        # Need to debug on PC
        if platform == 'android':
            self.path = '/storage/emulated/0/'
        else:
            self.path = 'C:/Coding/VFP/VFP/program/'
        self.file_filter = file_filter
        self.selected = ''

    def update(self, *args):
        """Update self width."""
        try:
            self.width = self.get_root_window().width
        except AttributeError:
            pass

        self.update_widgets()

    def update_widgets(self):
        """Updated viewed files and folders, current path."""
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

        # if not empty permiss scroll
        if self.children[0].children[0].children:
            self.children[0].scroll_y = 1

    def turn_back(self):
        """Return to last folder."""
        try:
            if (
                len(self.path.split('/')) > 2
                and
                self.path != '/storage/emulated/0/'
            ):
                self.path = '/'.join(self.path.split('/')[:-2]) + '/'
                self.selected = ''
                self.update_widgets()
        except PermissionError:
            pass

    def select(self, instance):
        """Select file."""
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
    """File manager item folder/icon."""

    def __init__(self, font_size, name, tp):
        """Set name, path and type of item."""
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
        """Select on touch."""
        if self.collide_point(*touch.pos):
            self.parent.parent.parent.select(self)


#
# Application
#
class App(MDApp):
    """Application class."""

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
    """Set max iteration to predict warnings. Run app."""
    Clock.max_iteration = 1000
    Window.softinput_mode = 'below_target'
    App().run()


if __name__ == '__main__':
    main()
