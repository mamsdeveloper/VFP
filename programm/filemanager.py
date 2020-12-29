import os
import sys
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivymd.uix.gridlayout import MDGridLayout

__all__ = ('FileManager', )


Builder.load_string(
"""
<FileManager>:
    bg_color: (1, 1, 1, 1)
    sub_color: (0, 0, 0, 1)
    radius: [0]
    path: ''

    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            pos: root.pos
            size: root.size
            radius: root.radius

    MDGridLayout:
        cols: 1
        adaptive_height: True
        spacing: root.width // 20

        MDGridLayout:
            cols: 2
            size_hint_y: None
            adaptive_height: True
            padding: [0, 0, root.width // 25, 0]
            spacing: root.width // 50

            canvas.before:
                Color:
                    rgba: root.sub_color
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [root.radius[0], root.radius[0], 0, 0]

            MDIconButton:
                icon: 'arrow-left'
                user_font_size: root.width // 10
                on_release: root.turn_back()

            MDLabel:
                size_hint_x: .7
                shorten: True
                font_size: root.width // 20
                text: root.path

        MDGridLayout:
            cols: 2
            size_hint: 1, None
            height: self.minimum_height
            spacing: self.width // 15


<FileManagerItem>:
    cols: 1
    adaptive_height: True
    name: ''
    icon: 'error'
    font_size: 10
    spacing: self.font_size // 10

    AnchorLayout:
        anchor_x: 'center'
        size_hint_y: None
        height: root.font_size

        MDIconButton:
            st: False
            user_font_size: root.font_size
            icon: root.icon
            on_release: root.parent.parent.parent.select(root)

            canvas.before:
                Color:
                    rgba: (1, 1, 1, .3) if self.st else (0, 0, 0, 0)
                RoundedRectangle:
                    pos: self.x + self.height//2-self.user_font_size*1.1//2, self.y + self.width//2-self.user_font_size*1.1//2
                    size: self.user_font_size*1.1, self.user_font_size*1.1
                    radius: [self.height*.1]

    
    AnchorLayout:
        anchor_x: 'center'
        size_hint: .5, None
        height: root.font_size // 4
        
        MDLabel:
            size_hint_x: None
            shorten: True
            halign: 'center'
            font_size: root.font_size // 4
            text: root.name
"""
)


class FileManager(ScrollView):
    def __init__(self, bg_color=(1, 1, 1, 1), sub_color=(0, 0, 0, 1), radius=0, file_filter=[]):
        super().__init__()
        self.bg_color = bg_color
        self.sub_color = sub_color
        self.radius = [radius]
        self.file_filter = file_filter
        self.path = 'C:/Coding/KivyLearning/'
        self.selected = ''
        self.update_widgets()
        

    def update_widgets(self):
        self.children[0].children[0].clear_widgets()

        list_dir = os.listdir(self.path)
        items_list = ['.kv']
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
                FileManagerItem(self.width*.18, item[0], item[1]))
    
    def turn_back(self):
        if self.path != 'C:/':
            self.path = '/'.join(self.path.split('/')[:-2]) + '/'
            self.update_widgets()

    def select(self, instance):
        if instance.tp == 'file':
            self.selected = self.path + instance.name
            for item in self.children[0].children[0].children:
                if self.path + item.name == self.selected:
                    item.children[1].children[0].st = True
                else:
                    item.children[1].children[0].st = False
                
        else:
            self.path = self.path + instance.name + '/'
            self.update_widgets()


class FileManagerItem(MDGridLayout):
    def __init__(self, font_size, name, tp):
        super().__init__()
        self.name = name
        self.tp = tp
        self.icon = 'file-outline' if self.tp == 'file' else 'folder-outline'
        self.font_size = font_size
