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

from exppanel import ExpPanel


#
# Screen managers and Screens
#
class AppScreenManager(ScreenManager):
    pass


# Screen that provide default properties for screens
class ParentScreen(MDScreen):
    def redirect(self, instance):
        print('>>>', instance.name)
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
    def save_settings(self, instance):
        print('>>> Save settings')
        self.redirect(instance)


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
    pass


class ExpPanelItemsList(MDGridLayout):
    def on_children(self, a, b):
        try:
            self.rad = b[0].height*.2
        except:
            pass

    def add_item(self):
        self.add_widget(ExpPanelItem('Класс'))

    def del_item(self, instance):
        self.remove_widget(instance)


class ExpRightButton(AnchorLayout):
    pass


class ExpPanelFirstItem(GridLayout):
    pass


class ExpPanelAddButton(AnchorLayout):
    pass


class ExpPanelItem(GridLayout):
    def __init__(self, placeholder=None, **kwargs):
        super().__init__(**kwargs)
        self.placeholder = placeholder

    def on_children(self, a, b):
        b[0].hint_text = 'Класс'


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

        sm.current = 'Settings'

        return sm  # return screen manager


# Running application
def main():
    Clock.max_iteration = 30
    VFP().run()


if __name__ == '__main__':
    main()
