from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.picker import MDDatePicker
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup

import requests
import json
import datetime as dt


from kivy.uix.progressbar import ProgressBar

# TODO: Change the result display for calc mode from textInputBox to label


# Set the app size
Window.size = (750,844)

# API Keys
API_key = "Your API Key"
Bearer_tax = "Your Bearer Key"

#global Var
calc_before = False
operator = ["*", "/", "-", "+"]
PopUp_yearly = 'There is error with the request'
PopUp_monthly = ''
PopUp_semi = ''
federal_tax = '0'
state_tax = '0'
fica_holding = '0'
Current_price = {}
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
    def Add_comma(self, text):
        arr = []
        i = len(text) - 1
        counter = 0
        while i >= 0:
            if counter == 3:
                arr.append(",")
                arr.append(text[i])
                counter = 0
            else:
                arr.append(text[i])
            counter += 1
            i -= 1
        if arr[-1] == ",":
            arr[-1] = ""
        return ''.join(reversed(arr))

    def remove_comma(self, text):
        new_text = []
        number_set = {"1","2","3","4","5","6","7","8","9","0"}
        for i in text:
            if i in number_set:
                new_text.append(i)
        
        return ''.join(new_text)

    def slide_value(self, *args):
        self.slide_text.text = F'$ {self.Add_comma(str(int(args[1])))}'

    def text_input(self):
        textIn = self.ids.slider_textInput.text
        if textIn == '' or textIn == '$ ' or textIn == '$':
            self.ids.slider_textInput.text = '$ '
            return
        self.ids.slider_input.value = float(self.remove_comma(textIn))


    def APIRequest(self, year, pay, st, filing, ex):
        url = f'https://stylinandy-taxee.p.rapidapi.com/v2/calculate/{year}'

        payload = f'filing_status={filing}&pay_rate={pay}&state={st}&exemptions={ex}&pay_periods=1'
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'authorization': Bearer_tax,
            'x-rapidapi-host': "stylinandy-taxee.p.rapidapi.com",
            'x-rapidapi-key': API_key
            }

        response = requests.request("POST", url, data=payload, headers=headers)
        if int(response.status_code) >= 400 and int(response.status_code) <= 600:
            print("Error: ", response.status_code)
            return -1
        return response

    def taxCalculate(self):
        global PopUp_yearly
        global PopUp_monthly
        global PopUp_semi
        global federal_tax
        global  state_tax
        global fica_holding
        dict_status = {"Single": "single",
                        "Married/RDP filing jointly":"married",
                        "Married/RDP filing separately":"marriedseparately",
                        "Head Of Household": "headof_household"}
                        
        year = self.ids.year_input.text
        pay_rate = self.remove_comma(self.slide_text.text)
        state = self.ids.state_input.text
        filing_status = self.ids.FilingStatus_input.text
        expts = self.ids.exemption_input.text
        
        if year == "Year" or len(pay_rate) == 0 or len(state) > 8 or filing_status not in dict_status or len(expts) > 4:
            print("something is not filled out...")
            return

        res = self.APIRequest(year, pay_rate, state, dict_status[filing_status], expts)

        print(res)
        if res == -1:
            PopUp_yearly = 'There is error with the request'
            PopUp_monthly = ''
            PopUp_semi = ''
            federal_tax = '0'
            state_tax = '0'
            fica_holding = '0'
            print("something is wrong...")
            return
        r = json.loads(res.text)
        json_readable = json.dumps(r, sort_keys=True, indent=4, separators=(',', ':'))
    
        print(json_readable)
        
        federal_tax = r["annual"]["federal"]["amount"]
        fica_holding = r["annual"]["fica"]["amount"]
        state_tax = r["annual"]["state"]["amount"]

        if state_tax is None:
            state_tax = '0'
            calculate = f'{pay_rate} - {federal_tax} - {fica_holding}'
        else:
            calculate = f'{pay_rate} - {federal_tax} - {state_tax} - {fica_holding}'
        # yearly will be counted with eval then converted to float
        # and lastly, it will get rounded before get converted back to str
        PopUp_yearly = str(round(float(eval(calculate)),2))
        PopUp_monthly = str(eval(f'{PopUp_yearly} / 12'))
        PopUp_semi = str(eval(f'{PopUp_monthly} / 2'))
        
class MyPopup(Popup):
    def Add_comma(self, text):
        convert = float(text)
        convert_text = str(round(convert, 2))
        arr = []
        i = len(convert_text) - 1
        counter = 0
        while i >= 0:
            if convert_text[i] == ".":
                counter = 0
                arr.append(convert_text[i])
            elif counter == 3:
                arr.append(convert_text[i])
                arr.append(",")
                counter = 0
            else:
                arr.append(convert_text[i])
            counter += 1
            i -= 1
        if arr[-1] == ",":
            arr[-1] = ""
        return ''.join(reversed(arr))

    def SetData(self):
        self.fed_tax.text = f'$ {self.Add_comma(federal_tax)}'
        self.state_tax.text = f'$ {self.Add_comma(state_tax)}'
        self.fica_tax.text = f'$ {self.Add_comma(fica_holding)}'
        # this if statement to tell the user if something is wrong
        if len(PopUp_yearly) > 30:
            self.ids.pop_yearly.text = PopUp_yearly
            return
        self.ids.pop_yearly.text = f'$ {self.Add_comma(PopUp_yearly)}'
        self.ids.pop_monthly.text = f'$ {self.Add_comma(PopUp_monthly)}'
        self.ids.pop_semi.text = f'$ {self.Add_comma(PopUp_semi)}'
      

class Exchange(Screen):

    options = {
        "SGD": 'Images/Singapore.png',
        "MYR": 'Images/Malaysia.png',
        "EUR": 'Images/Euro.png',
        "USD": 'Images/USA.png',
        "AUD": 'Images/Australia.png',
        "JPY": 'Images/Japan.png',
        "CNH": 'Images/China.png',
        "HKD": 'Images/HongKong.png',
        "CAD": 'Images/Canada.png',
        "INR": 'Images/India.png',
        "DKK": 'Images/Denmark.png',
        "GBP": 'Images/UK.png',
        "RUB": 'Images/Russia.png',
        "NZD": 'Images/NZ.png',
        "MXN": 'Images/Mexico.png',
        "IDR": 'Images/Indonesia.png',
        "TWD": 'Images/Taiwan.png',
        "THB": 'Images/Thailand.png',
        "VND": 'Images/Vietnam.png'
    }
    # this function works when we dont allow the user to enter more than 2
    # decimal point. needs to be developed to handle all scenario.
    # may be we can scan from left to right to find the '.' 
    # if we find it then just append without having to worry about comma
    # once we pass that its business as usual.
    def Adding_comma(self, text):
        arr = []
        i = len(text) - 1
        counter = 0
        while i >= 0:
            if text[i] == ".":
                counter = 0
                arr.append(".")
                i -= 1
                continue
            elif counter ==  3 :
                arr.append(",")
                arr.append(text[i])
                counter = 0
            else:
                arr.append(text[i])
            counter += 1
            i -= 1
        if arr[-1] == ",":
            arr[-1] = ""
        return ''.join(reversed(arr))

    def remove_comma(self, text):
        new_text = []
        number_set = {"1","2","3","4","5","6","7","8","9","0","."}
        for i in text:
            if i in number_set:
                new_text.append(i)
        
        return ''.join(new_text)

    def dot(self):
        prior = self.ids.exchange_from.text
        if "." in prior:
            pass
        else:
            # Add a decimal to the end of the text
            prior = f'{prior}.'
            # Output back to the text box
            self.ids.exchange_from.text = prior

    def clear(self):
        self.ids.exchange_from.text = '0'
        self.ids.exchange_to.text = '0'

    def backSpace(self):
        if len(self.ids.exchange_from.text) == 1:
            self.ids.exchange_from.text = '0'
            self.ids.exchange_to.text = '0'
            return
        backSpace = self.ids.exchange_from.text[:-1]
        backSpace = self.remove_comma(backSpace)
        self.ExchangeCalculate(backSpace)
        backSpace = self.Adding_comma(backSpace)
        self.ids.exchange_from.text = backSpace

    def switch(self):
        holder_from = self.ids.spinner_from.text
        self.ids.spinner_from.text = self.ids.spinner_to.text
        self.ids.spinner_to.text = holder_from

        self.Calculate_exchange('')
        return

    def Calculate_exchange(self, button):
        prior = self.remove_comma(self.ids.exchange_from.text)
        print(prior)
        if len(prior) > 3 and prior[-3] == '.':
            return

        if len(prior) > 10:
            return
        if prior == '0':
            print("im here")
            print("im here with button ", button , " and prior ", prior)
            self.ids.exchange_from.text = str(button)
            self.ExchangeCalculate(str(button))
            return

        prior = f'{prior}{button}'
        self.ExchangeCalculate(prior)

        if len(prior) > 3:
            self.ids.exchange_from.text = self.Adding_comma(prior)
        else:
            self.ids.exchange_from.text = prior

    def ExchangeCalculate(self, exchg_input):
        if exchg_input == '':
            self.ids.exchange_from.text = '0'
            return

        url = "https://currency-exchange.p.rapidapi.com/exchange"

        querystring = {"from":self.ids.spinner_from.text,"to":self.ids.spinner_to.text,"q":"1.0"}

        headers = {
            'x-rapidapi-host': "currency-exchange.p.rapidapi.com",
            'x-rapidapi-key': API_key
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        # result = str(round(float(eval(f'{response.text} * {exchg_input}')),2))
        result = eval(f'{response.text} * {exchg_input}')
        
        result = self.Add_comma(result)
        
        self.ids.exchange_to.text = f'{result}'

    def Add_comma(self, text):
        convert = float(text)
        convert_text = str(round(convert, 2))
        arr = []
        i = len(convert_text) - 1
        counter = 0
        while i >= 0:
            if convert_text[i] == ".":
                counter = 0
                arr.append(convert_text[i])
            elif counter == 3:
                arr.append(convert_text[i])
                arr.append(",")
                counter = 0
            else:
                arr.append(convert_text[i])
            counter += 1
            i -= 1
        if arr[-1] == ",":
            arr[-1] = ""
        return ''.join(reversed(arr))
class getDate(Screen):
    AddOrSub = ''
    chosen_date = ''
    Mode = ''
    from_date = ''
    to_date = ''
    def marked(self, instance, value, calc):
        if value:
            self.AddOrSub = calc
            print('The checkbox' ,'is active', self.AddOrSub)
        else:
            print('The checkbox', 'is inactive')


    def mode_marked(self, instance, value, calc):
        self.Mode = calc
        if calc == 'calc':

            self.ids.PickFromdate.text = 'Pick the date'
            self.ids.PickFromdate.opacity = 1
            self.ids.PickFromdate.disabled = False

            self.ids.pickToDate.opacity = 0
            self.ids.pickToDate.disabled = True

            self.ids.add_1.opacity = 1

            self.ids.add_2.opacity = 1
            self.ids.add_2.disabled = False

            self.ids.add_3.opacity = 1

            self.ids.add_4.opacity = 1
            self.ids.add_4.disabled = False
        else:
            self.ids.PickFromdate.text = 'From Date'
            self.ids.pickToDate.text = 'To Date'

            self.ids.PickFromdate.opacity = 1
            self.ids.PickFromdate.disabled = False

            self.ids.pickToDate.opacity = 1
            self.ids.pickToDate.disabled = False

            self.ids.add_1.opacity = 0

            self.ids.add_2.opacity = 0
            self.ids.add_2.disabled = True

            self.ids.add_3.opacity = 0

            self.ids.add_4.opacity = 0
            self.ids.add_4.disabled = True

    def on_save(self, instance, value, date_range):
        week_days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        get_day = str(value).split("-")
        self.chosen_date = get_day
        self.from_date = f'{get_day[1]}/{get_day[2]}/{get_day[0][2:]}'

        week_num = dt.date(int(get_day[0]),int(get_day[1]),int(get_day[2])).weekday() 
        self.ids.PickFromdate.text = f'{week_days[week_num]} {str(value)}'
		
    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def on_save_to(self, instance, value, date_range):
        week_days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        get_day = str(value).split("-")
        self.to_date = f'{get_day[1]}/{get_day[2]}/{get_day[0][2:]}'
        week_num = dt.date(int(get_day[0]),int(get_day[1]),int(get_day[2])).weekday() 
        self.ids.pickToDate.text = f'{week_days[week_num]} {str(value)}'

    def show_date_picker_to(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save_to)
        date_dialog.open()

    def getHowLong(self):
        if self.Mode == 'calc':
            if self.ids.PickFromdate.text == 'Pick the date':
                self.ids.SumDate.text = "Please pick the date"
            else:
                self.addOrSubCalc()
        elif self.Mode == 'range':
            if self.ids.PickFromdate.text == 'From Date' or self.ids.pickToDate.text == 'To Date':
                self.ids.SumDate.text = f'Please enter the date'
            else:
                # if we get the valid values calculate here
                difference_days = str(self.days_between())
                convertResult = self.convertDays(difference_days)
                if convertResult[0] > 0:
                    self.ids.SumDate.text = f'The difference between two date is {convertResult[0]} years, {convertResult[1]} weeks and {convertResult[2]} days'
                elif convertResult[1] > 0:
                    self.ids.SumDate.text = f'The difference between two date is  {convertResult[1]} weeks and {convertResult[2]} days'
                else:
                    self.ids.SumDate.text = f'The difference between two date is  {convertResult[2]} days'
        else:
            self.ids.SumDate.text = f'Please select something'
            return

    # use python function to calculate the difference between 2 date
    def days_between(self):
        d1 = self.from_date
        d2 = self.to_date
        dayFrom = dt.datetime.strptime(d1, "%m/%d/%y")
        dayTo = dt.datetime.strptime(d2, "%m/%d/%y")
        return abs((dayTo - dayFrom).days)

    def convertDays(self, days):
        days = int(days)
        weeks = days // 7
        days = days % 7
        year = 0
        if weeks >= 52:
            year = weeks // 52
            weeks = weeks % 52
        
        return (year, weeks, days)
        # #TODO: convert days given to years, weeks and days.
        # return

    def addOrSubCalc(self):
        week_days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        final_arr = []
        calc_day = self.chosen_date
        
        #substract date calculation
        if self.AddOrSub == "Substract":
            get_year = int(calc_day[0]) - int(self.ids.year_input.text)
            get_month = int(calc_day[1]) - int(self.ids.month_input.text)
            if get_month <= 0:
                extra_year = 1 + (abs(get_month) // 12)
                get_year -= extra_year
                get_month = 12 - (abs(get_month) % 12)

            startDate = f'{get_month}/{calc_day[2]}/{str(get_year)[2:]}'
            date_1 = dt.datetime.strptime(startDate, "%m/%d/%y")
            end_date = date_1 - dt.timedelta(days=int(self.ids.day_input.text))
            final_arr = str(end_date).split("-")
        # add date calculation
        else:
            get_year = int(calc_day[0]) + int(self.ids.year_input.text)
            get_month = int(calc_day[1]) + int(self.ids.month_input.text)

            if get_month > 12:
                extra_year = get_month // 12
                get_year += extra_year
                get_month = get_month - (extra_year * 12)
            startDate = f'{get_month}/{calc_day[2]}/{str(get_year)[2:]}'
            date_1 = dt.datetime.strptime(startDate, "%m/%d/%y")
            end_date = date_1 + dt.timedelta(days=int(self.ids.day_input.text))
            final_arr = str(end_date).split("-")

        #After the calculation we get the date and display to user
        week_num = dt.date(int(final_arr[0]),int(final_arr[1]),int(final_arr[2][:2])).weekday() 
        self.ids.SumDate.text = f'{week_days[week_num]}, {final_arr[0]}-{final_arr[1]}-{final_arr[2][:2]}'
        print(self.ids.SumDate.text)

class CalculatorApp(MDApp):
    def build(self):
        Window.clearcolor = (1,1,1,1)
        sm = ScreenManager()
        sm.add_widget(Calculator(name = 'Calculator'))
        sm.add_widget(EstimateIncome(name = 'estimate'))
        sm.add_widget(Exchange(name='Exchange'))
        sm.add_widget(getDate(name='date'))
        return sm

if __name__ == '__main__':
    CalculatorApp().run()








