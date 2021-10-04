from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty
from kivy.uix.popup import Popup
import requests
import json


from kivy.uix.progressbar import ProgressBar




# Set the app size
# Window.size = (500,700)
Window.size = (1000,1000)

# Designate Our .kv design file 
# Builder.load_file('calculator.kv')
calc_before = False
operator = ["*", "/", "-", "+"]

PopUp_yearly = '123'
PopUp_monthly = ''
PopUp_semi = ''
class Calculator(Screen):
    # clear screen function
    def clear(self):
        self.ids.calc_input.text = '0'

    # button pressing function
    def button_press(self, button):
        global calc_before
        # create a variable that contains whatever was in the text box already
        prior = self.ids.calc_input.text
        
        # determine if 0 is sitting there
        if prior == "0":
            self.ids.calc_input.text = ''
            self.ids.calc_input.text = f'{button}'
        elif calc_before and prior[-1] not in operator:
            calc_before = False
            self.ids.calc_input.text = ''
            self.ids.calc_input.text = f'{button}'
        else: 
            self.ids.calc_input.text = f'{prior}{button}'
            calc_before = False
    
    # remove last character in text box
    def remove(self):
        prior = self.ids.calc_input.text
        # Remove The last item in the textbox
        prior = prior[:-1]
        # Output back to the textbox
        self.ids.calc_input.text = prior
    
    # make text box positive or negative
    def pos_neg(self):
        prior = self.ids.calc_input.text
        # Test to see if there's a - sign already
        if "-" in prior:
             self.ids.calc_input.text = f'{prior.replace("-", "")}'
        else:
            self.ids.calc_input.text = f'-{prior}'

    # decimal function
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
        last_operator = curr[-1]
        # check to make sure that operator sign wont be next to each other
        if last_operator in operator:
            temp_list = list(curr)
            temp_list[-1] = sign
            curr = ''.join(temp_list)
        else:
            curr = f'{curr}{sign}'
        
        self.ids.calc_input.text = curr

    def equals(self):
        global calc_before
        prior = self.check_text(self.ids.calc_input.text)

        if prior == "Error":
            self.ids.calc_input.text = "Error"
        else:
            self.ids.calc_input.text = str(eval(prior))
            calc_before = True

    def check_text(self, text):
        # this check is to ensure that we have pass in valid calculation
        if text[-1] in operator:
            text = f'{text}{text[:-1]}'
            return text
        # check for division by 0 and throw an error if found
        for i in range(len(text)):
            if text[i] == "/" and i < len(text):
                if text[i + 1] == "0":
                    return "Error"
        return text
                     
class EstimateIncome(Screen):
    def GetFederalIncomeTaxInfo(self):
        url = "https://stylinandy-taxee.p.rapidapi.com/v2/federal/2020"
        headers = {
            'authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJBUElfS0VZX01BTkFHRVIiLCJodHRwOi8vdGF4ZWUuaW8vdXNlcl9pZCI6IjU3Y2IyMWE2YmI4N2MxMDA0NGE2NmE2MiIsImh0dHA6Ly90YXhlZS5pby9zY29wZXMiOlsiYXBpIl0sImlhdCI6MTQ3MzAxODA1OX0.xkn1_LHnLijhYMONl5iXhKD1vsdm0_5AtSKGsPrVtxI",
            'x-rapidapi-host': "stylinandy-taxee.p.rapidapi.com",
            'x-rapidapi-key': "YOUR API KEY"
            }
        response = requests.request("GET", url, headers=headers)
        r = json.loads(response.text)
        json_readable = json.dumps(r, sort_keys=True, indent=4, separators=(',', ':'))
        
    def GetStateIncomeTax(self):
        url = "https://stylinandy-taxee.p.rapidapi.com/v2/state/2020/CA"

        headers = {
            'authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJBUElfS0VZX01BTkFHRVIiLCJodHRwOi8vdGF4ZWUuaW8vdXNlcl9pZCI6IjYxNWEzNjJkMTQ3NjM1M2NkYjg4MGI1ZCIsImh0dHA6Ly90YXhlZS5pby9zY29wZXMiOlsiYXBpIl0sImlhdCI6MTYzMzMwMjA2MX0.dbskM2DS-9eCFAc_MHGiyfOklBaXVYrJ5JZimQtiPvg",
            'x-rapidapi-host': "stylinandy-taxee.p.rapidapi.com",
            'x-rapidapi-key': "YOUR API KEY"
            }

        response = requests.request("GET", url, headers=headers)
        r = json.loads(response.text)
        json_readable = json.dumps(r, sort_keys=True, indent=4, separators=(',', ':'))
        print(response.text)

    def taxCalculate(self):
        '''
        Needs Year, filing status, payrate, state, exemptions

        '''
        year = 2020
        pay_rate = 87000
        state = 'MS'

        pay_rate = self.ids.income_input.text
        state = self.ids.state_input.text

        
        filing_status = 'single'

        url = f'https://stylinandy-taxee.p.rapidapi.com/v2/calculate/{year}'

        # this one is with exemption
        # payload = "filing_status=single&pay_rate=150000&state=CA&exemptions=1&pay_periods=1"

        payload = f'filing_status=single&pay_rate={pay_rate}&state={state}&pay_periods=1'
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJBUElfS0VZX01BTkFHRVIiLCJodHRwOi8vdGF4ZWUuaW8vdXNlcl9pZCI6IjYxNWEzNjJkMTQ3NjM1M2NkYjg4MGI1ZCIsImh0dHA6Ly90YXhlZS5pby9zY29wZXMiOlsiYXBpIl0sImlhdCI6MTYzMzMwMjA2MX0.dbskM2DS-9eCFAc_MHGiyfOklBaXVYrJ5JZimQtiPvg",
            'x-rapidapi-host': "stylinandy-taxee.p.rapidapi.com",
            'x-rapidapi-key': "YOUR API KEY"
            }

        response = requests.request("POST", url, data=payload, headers=headers)

        r = json.loads(response.text)
        json_readable = json.dumps(r, sort_keys=True, indent=4, separators=(',', ':'))

        print(json_readable)
        federal_tax = r["annual"]["federal"]["amount"]
        fica_holding = r["annual"]["fica"]["amount"]
        state_tax = r["annual"]["state"]["amount"]
        calculate = f'{pay_rate} - {federal_tax} - {state_tax} - {fica_holding}'
        global PopUp_yearly
        global PopUp_monthly
        global PopUp_semi

        self.ids.yearly.text = str(eval(calculate))
        self.ids.monthly.text = str(eval(f'{self.ids.yearly.text} / 12'))
        self.ids.semi.text = str(eval(f'{self.ids.monthly.text} / 2'))

        PopUp_yearly = self.ids.yearly.text
        PopUp_monthly = self.ids.monthly.text
        PopUp_semi = self.ids.semi.text
        
        self.ids.yearly.text = f'$ {self.ids.yearly.text}'
        self.ids.monthly.text = f'$ {self.ids.monthly.text}'
        self.ids.semi.text = f'$ {self.ids.semi.text}'

class MyPopup(Popup):
    def SetData(self):
        
        self.ids.pop_yearly.text = f'$ {PopUp_yearly}'
        self.ids.pop_monthly.text = f'$ {PopUp_monthly}'
        self.ids.pop_semi.text = f'$ {PopUp_semi}'
        

class Get_Date(Screen):
    pass

class CalculatorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Calculator(name = 'Calculator'))
        sm.add_widget(EstimateIncome(name = 'estimate'))
        sm.add_widget(Get_Date(name='getDate'))
        
        return sm

if __name__ == '__main__':
    CalculatorApp().run()