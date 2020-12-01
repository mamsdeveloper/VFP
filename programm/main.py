from kivymd.app import MDApp
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDRectangleFlatButton
from kivy.uix.textinput import TextInput

# Changing direction of Screen's swipe
def swipe_direction(self, instance):
    if instance.pos[0]<=self.width/2:
        self.parent.transition.direction = 'right'
    else:
        self.parent.transition.direction = 'left'

# Screen managers and Screens
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


# Work Areas
class ParentArea(GridLayout):
    pass
    # def __init__(self, **kwargs):
    #    super().__init__(**kwargs)


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


# Application
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

        return sm # return screen manager

    

# Running application
def main():
    """
    Config.set('graphics', 'resizable', False)
    Config.set('graphics', 'width', 320)
    Config.set('graphics', 'height', 650)
    Config.set('graphics', 'default_font', [
                                            'Roboto', 
                                            'data/fonts/Roboto-Regular.ttf',
                                            'data/fonts/Roboto-Italic.ttf', 
                                            'data/fonts/Roboto-Bold.ttf', 
                                            'data/fonts/Roboto-BoldItalic.ttf'
                                            ])
    Config.write()
    """

    VFP().run()

if __name__ == '__main__':
    main()
