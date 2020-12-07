from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.graphics import (Color, RoundedRectangle)
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.button import MDIconButton
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock

Clock.max_iteration = 30


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


class MyApp(MDApp):
    def add_exp(self):
        self.root.children[1].add_widget(ExpPanel())
        # close exps
        for exp in self.root.children[1].children:
            if exp.st:
                exp.change_state()

    def del_exp(self, instance):
        self.root.children[1].remove_widget(instance.parent.parent)


def main():
    app = MyApp()
    app.run()


if __name__ == '__main__':
    main()
