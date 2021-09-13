from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

red = [1, 0, 0, 1]
green = [0, 1, 0, 1]
blue = [0, 0, 1, 1]
purple = [1, 0, 1, 1]

class MainApp(App):
    # def build(self):
    #     label = Label(text="Hello from kivy",
    #                    size_hint=(.05, .05),
    #                    pos_hint={'center_x': .5, 'center_y': .5})
                       
        
    #     return label

    def build(self):
        layout = BoxLayout(padding = 10)
        
        return img


if __name__ == '__main__':
    app = MainApp()
    app.run()