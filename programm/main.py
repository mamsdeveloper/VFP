from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.button import MDIconButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.screen import MDScreen
from config_utils import *


#
# Screen managers and Screens
#
class AppScreenManager(ScreenManager):
    pass


# Screen that provide default properties for screens
class ParentScreen(MDScreen):
    def redirect(self, instance):
        print('>>> Redirect to', instance.name)
        # create settings
        if self.name == 'Main' and instance.name == 'Settings':
            self.parent.screens[-1].apply_config()

        # change swipe mod
        swipe_direction(self, instance)
        # change screen
        self.parent.current = instance.name


class MainScreen(ParentScreen):
    def open_file(self, instance):
        print('>>> Open File')
        self.redirect(instance)


class CreateScreen(ParentScreen):
    pass


class UpdateScreen(ParentScreen):
    pass


class ViewScreen(ParentScreen):
    pass


class SettingsScreen(ParentScreen):
    # set default settings
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.apply_config()

    # change widgets using config

    def apply_config(self):
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

        # groups
        all_widgets.children[1].clear_widgets()

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

            all_widgets.children[1].add_widget(exp)

        del config, all_widgets, teacher_list, exp, exp_item, item

    def save_settings(self, instance):
        print('>>> Save settings')
        save_config(self)
        self.redirect(instance)


class ClassScreen(ParentScreen):
    def __init__(self, instance, students=[], **kwargs):
        super().__init__(**kwargs)
        # what item create this screen
        self.instance = instance
        # add student in box
        self.students = students
        self.student_box = self.children[0].children[1].children[0].children[1]

        # create exist students
        for student in self.students:
            self.student_box.add_widget(StudentItem(student))

    # reinit parent method to remove self after redirect and update students list

    def redirect(self, instance):
        super().redirect(instance)
        # remove from screen manager
        self.remove_self()

        # update and give students list
        self.update_students()
        self.instance.students = self.students

    # remove self from sm

    def remove_self(self):
        self.parent.remove_widget(self)

    # get students names

    def update_students(self):
        self.students = []
        for item in self.student_box.children:
            # validate
            if item.children[1].children[0].text:
                self.students.append(item.children[1].children[0].text)

        self.students.sort()


# Changing direction of Screen's swipe
def swipe_direction(self, instance):
    if instance.pos[0] <= self.width/2:
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


class FileSettingsArea(ParentArea):
    pass


class FileWriteArea(ParentArea):
    pass


class FileViewArea(ParentArea):
    pass


#
# Expansion Panel
#
class ExpsList(MDGridLayout):
    def add_exp(self):
        self.add_widget(ExpPanel())
        # close exps
        for exp in self.children:
            if exp.st:
                exp.change_state()

    def del_exp(self, instance):
        self.remove_widget(instance.parent.parent)


class ExpPanel(MDGridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # init box and right button
        self.add_widget(ExpPanelBox())
        self.add_widget(ExpRightButton())

        # init items list
        self.items_list = ExpPanelItemsList()

        # add first item, items list and add-button in box
        self.children[1].add_widget(ExpPanelFirstItem())

        # self close/open state
        self.st = False

    # Change state of exp (close or open)
    def change_state(self):
        # close
        if self.st:
            self.children[1].remove_widget(self.items_list)
            self.children[1].remove_widget(self.children[1].children[0])

            self.children[1].children[0].children[0].icon = 'menu-right'
        else:
            # open
            # close others exps
            for exp in self.parent.children:
                if exp != self and exp.st:
                    exp.change_state()

            self.children[1].add_widget(self.items_list)
            self.children[1].add_widget(ExpPanelAddButton())

            self.children[1].children[2].children[0].icon = 'arrow-down-drop-circle'

        self.st = not self.st


class ExpPanelBox(MDGridLayout):
    def on_children(self, none, children):
        self.rad = children[0].height*.2


class ExpPanelItemsList(MDGridLayout):
    def add_item(self):
        self.add_widget(ExpPanelItem())

    def del_item(self, instance):
        self.remove_widget(instance)


class ExpRightButton(AnchorLayout):
    pass


class ExpPanelFirstItem(GridLayout):
    pass


class ExpPanelAddButton(AnchorLayout):
    pass


class ExpPanelItem(GridLayout):
    def update_class(self, instance):
        # create class screen
        self.class_scr = ClassScreen(self, self.students, name=instance.text)
        # add screen in screen manager
        sm = self.parent.parent.parent.parent.parent.parent.parent.parent.parent
        sm.add_widget(self.class_scr)
        sm.transition.direction = 'left'
        sm.current = instance.text

        del sm


#
# Area's items
#
class StudentsList(MDGridLayout):
    def add_student(self):
        self.add_widget(StudentItem())

    def del_student(self, instance):
        self.remove_widget(instance)


class StudentItem(GridLayout):
    def __init__(self, text='', **kwargs):
        super().__init__(**kwargs)
        self.text = text


#
# Application
#
class VFP(MDApp):
    def build(self):
        # Appd settings
        self.title = 'ВФП'
        self.icon = '..\\data\\logo.png'
        self.theme_cls.primary_palette = 'Gray'
        # Screens
        self.main_scr = MainScreen(name='Main')
        self.create_scr = CreateScreen(name='Create')
        self.update_scr = UpdateScreen(name='Update')
        self.view_scr = ViewScreen(name='View')
        self.settings_scr = SettingsScreen(name='Settings')
        # Create SM
        sm = AppScreenManager()
        sm.add_widget(self.main_scr)
        sm.add_widget(self.create_scr)
        sm.add_widget(self.update_scr)
        sm.add_widget(self.view_scr)
        sm.add_widget(self.settings_scr)

        sm.current = 'Main'

        return sm  # return screen manager

# Running application


def main():
    Clock.max_iteration = 1000
    app = VFP()
    app.run()


if __name__ == '__main__':
    main()
