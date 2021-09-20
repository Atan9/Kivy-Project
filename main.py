from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

# Set the app size
Window.size = (500,700)

# Designate Our .kv design file 
Builder.load_file('calculator.kv')

class MyLayout(Screen):
    def clear(self):
        self.ids.calc_input.text = '0'

    # Create a button pressing function
    def button_press(self, button):
        # create a variable that contains whatever was in the text box already
        prior = self.ids.calc_input.text
        
        # determine if 0 is sitting there
        if prior == "0":
                self.ids.calc_input.text = ''
                self.ids.calc_input.text = f'{button}'
        else: 
            self.ids.calc_input.text = f'{prior}{button}'
    
    # remove last character in text box
    def remove(self):
        prior = self.ids.calc_input.text
        # Remove The last item in the textbox
        prior = prior[:-1]
        # Output back to the textbox
        self.ids.calc_input.text = prior
    
    # Create function to make text box positive or negative
    def pos_neg(self):
        prior = self.ids.calc_input.text
        # Test to see if there's a - sign already
        if "-" in prior:
             self.ids.calc_input.text = f'{prior.replace("-", "")}'
        else:
            self.ids.calc_input.text = f'-{prior}'

    # Create decimal function
    def dot(self):
        prior = self.ids.calc_input.text
        
        if "." in prior:
            pass
        else:
            # Add a decimal to the end of the text
            prior = f'{prior}.'
            # Output back to the text box
            self.ids.calc_input.text = prior

    # create addition function
    def math_sign(self, sign):
        curr = self.ids.calc_input.text
        operator = ["*", "/", "-", "+"]
        last_operator = curr[-1]
        # check to make sure that operator sign wont be next to each other
        if last_operator in operator:
            temp_list = list(curr)
            temp_list[-1] = sign
            curr = ''.join(temp_list)
        else:
            curr = curr + sign
        
        self.ids.calc_input.text = curr


    def equals(self):
        prior = self.check_text(self.ids.calc_input.text)

        if prior == "Error":
            self.ids.calc_input.text = "Error"
        else:
            self.ids.calc_input.text = str(eval(prior))

    def check_text(self, text):
        divide = False
        operator = ["*", "/", "-", "+"]
        # this check is to ensure that we have pass in valid calculation
        if text[-1] in operator:
            text = text + text[:-1]
            return text
        # check for division by 0 and throw an error if found
        for i in range(len(text)):
            if text[i] == "/" and i < len(text):
                if text[i + 1] == "0":
                    return "Error"
        
        return text
                     
                

class EstimateIncome(Screen):
    pass



    # # create equals to function
    # def equals(self):
    #     prior = self.ids.calc_input.text
    #     print(prior)
    #     # Addition
    #     if "+" in prior:
    #         num_list = prior.split("+")
    #         answer = 0.0
    #         # loop thru our list
    #         for number in num_list:
    #             answer = answer + float(number)

    #         # print the answer in the text box
    #         self.ids.calc_input.text = str(answer)


class CalculatorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MyLayout(name = 'menu'))
        sm.add_widget(EstimateIncome(name = 'estimate'))
        return sm

if __name__ == '__main__':
    CalculatorApp().run()
