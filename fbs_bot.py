# -- TELEBOT IMPORTS -- #
import telebot
from telebot import types
from datetime import date, time, datetime, timedelta
# calendar link
# https://github.com/artembakhanov/python-telegram-bot-calendar/blob/master/examples/simple_pytelegrambotapi.py
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
# tutorial link
# https://github.com/eternnoir/pyTelegramBotAPI#getting-started

# -- LOGGING FOR TELEBOT -- #
import logging
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

# -- SELENIUM IMPORTS -- #
from selenium import webdriver
# pip install webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager
# implicit waits
import time
# import ActionChains for drag and drop
from selenium.webdriver import ActionChains
# import explicit waits
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# exceptions
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
# import select (for time)
from selenium.webdriver.support.ui import Select

##################################### -- SELENIUM HELPER FUNCTIONS -- #####################################
def login(driver, userName, passWord):
    user = driver.find_element_by_id("userNameInput").send_keys(userName)
    pw = driver.find_element_by_id("passwordInput").send_keys(passWord)
    submitButton = driver.find_element_by_id("submitButton").click()


def getDate(days): # dd-STR-yyyy
    from datetime import date, time, datetime, timedelta

    monthDict = {'01':'Jan',
                    '02': 'Feb',
                    '03': 'Mar',
                    '04': 'Apr',
                    '05': 'May',
                    '06': 'Jun',
                    '07': 'Jul',
                    '08': 'Aug',
                    '09': 'Sep',
                    '10': 'Oct',
                    '11': 'Nov',
                    '12': 'Dec'
    }

    today = date.today()
    delta = timedelta(days)
    setDate = today + delta

    parts = str(setDate).split('-') # YYYY - MM - DD
    parts[1] = monthDict[parts[1]]

    newFormat = parts[2] + '-' + parts[1] + '-' + parts[0]
    return newFormat

def getDatetime(timeStr, delta): # gives mm/dd/yyyy xx:x0:00 A/PM string format, delta is user.date_delta
    from datetime import date, time, datetime, timedelta

    today = date.today()
    delta = timedelta(delta)
    setDate = today + delta

    parts = str(setDate).split('-') # YYYY - MM - DD

    newFormat = str(int(parts[1])) + '/' + str(int(parts[2])) + '/' + parts[0] + ' ' + timeStr
    return newFormat


def addBooker(driver, name):
    import time
    addBookerBtn = driver.find_element_by_xpath('//*[@id="bookingFormControl1_GridCoBookers_ctl14"]').click()
    time.sleep(1.5)
    watermark = driver.find_element_by_xpath('//*[@id="bookingFormControl1_DialogSearchCoBooker_searchPanel_textBox"]/div/div/span/input[2]').click()
    inputName = driver.find_element_by_xpath('//*[@id="bookingFormControl1_DialogSearchCoBooker_searchPanel_textBox_c1"]').send_keys(name) 
    searchBtn = driver.find_element_by_xpath('//*[@id="bookingFormControl1_DialogSearchCoBooker_searchPanel_buttonSearch"]').click()
    time.sleep(1.5)
    confirmCheckbox = driver.find_element_by_xpath('//*[@id="bookingFormControl1_DialogSearchCoBooker_searchPanel_gridView_gv_ctl02_checkMultiple"]').click()
    confirmSelectBtn = driver.find_element_by_xpath('//*[@id="bookingFormControl1_DialogSearchCoBooker_dialogBox_b1"]').click()

def book(driver, co_bookers):
    for b in co_bookers:
        addBooker(driver, b)
        time.sleep(1)

##################################### -- END OF SELENIUM HELPER FUNCTIONS -- #####################################


# Enter your TELEBOT API KEY here within the ""
bot = telebot.TeleBot("", parse_mode=None) # Can set parse_mode by default. HTML or MARKDOWN


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Hello! Welcome to SMUFBS_bot by @chewyixinn\n\nType /book to get started.')


# @bot.message_handler(commands=['help']) # Add commands here
# def display_commands(message):
#     # display all the commmands here
#     # /help
#     # /startbooking
#     # /
#     pass


user_dict = {}
class User:
    def __init__(self,chat_id):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.login = False
        self.username = ''
        self.password = ''
        self.date_delta = ''
        self.buildingType = ''
        self.facilityType = ''
        self.co_bookers = []
        self.startTime = None
        self.endTime = None


@bot.message_handler(commands=['book'])
def getUsername(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "To start booking, please type your email.\n(e.g. john.doe.2020@sis.smu.edu.sg)")
    bot.register_next_step_handler(msg, getPassword)


def getPassword(message):
    chat_id = message.chat.id
    parts = message.text.split('@')
    if message.text == '/exit':
        msg = bot.reply_to(message, 'Sucessfully ended. Type in anything to restart.')
        bot.register_next_step_handler(msg, send_welcome)
    elif not(parts[0][-4:].isdigit() and len(parts[1]) > 10 and message.text[-10:] == "smu.edu.sg" and '@' in message.text and len(parts) == 2):
        msg = bot.send_message(chat_id, f"Invalid format, please re-enter username or type /exit to exit.")
        bot.register_next_step_handler(msg, getPassword)
    else:
        username = message.text        
        user = User(username)
        user_dict[chat_id] = user
        user.username = username
        msg = bot.send_message(chat_id, 'Please enter your password:')
        bot.register_next_step_handler(msg, confirmDetails)


def confirmDetails(message):
    chat_id = message.chat.id
    pw = message.text
    user = user_dict[chat_id]
    user.password = pw
    user.password_hidden = len(pw)*'*'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    itembtna = types.KeyboardButton('Yes, confirm.')
    itembtnb = types.KeyboardButton('No, re-enter details.')
    itembtnc = types.KeyboardButton('Exit programme.')
    markup.row(itembtna)
    markup.row(itembtnb)
    markup.row(itembtnc)   
    msg = bot.send_message(chat_id, "Confirm details?", reply_markup=markup)

    bot.register_next_step_handler(msg, detailsConfirmation)


def detailsConfirmation(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    msg = message.text
    if msg == 'Exit programme.':
        msg = bot.reply_to(message, 'Sucessfully ended. Type in anything to restart.')
        bot.register_next_step_handler(msg, send_welcome)
        user.driver.quit()
    elif msg == 'No, re-enter details.':
        msg = bot.reply_to(message, 'Restarting...')
        user.driver.quit()
        getUsername(msg)
    elif msg == 'Yes, confirm.':
        username = user.username
        password = user.password
        driver = user.driver
        bot.send_message(chat_id, "Logging in, please wait a moment...")
        driver.maximize_window()
        driver.get("https://fbs.intranet.smu.edu.sg/home")
        login(driver, username, password)
        try:
            driver.find_element_by_xpath('//*[@id="errorText"]')
            bot.reply_to(message, f"Incorrect user ID or password. Type the correct user ID and password, and try again.")
            msg = bot.send_message(chat_id, f"Please enter your email again: ")
            bot.register_next_step_handler(msg, getPassword)
            driver.quit()
        except NoSuchElementException:
            today = '-'.join(str(date.today()).split('-')[::-1])
            bot.send_message(chat_id, "Login successful!")
            user.login = True
            bot.send_message(chat_id, f"Today is {today}, which date would you like to book a facility on?\n\nClick on /setdate type /setdate.")
    else:
        msg = bot.reply_to(message, "Invalid input.")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtna = types.KeyboardButton('Yes, confirm.')
        itembtnb = types.KeyboardButton('No, re-enter details.')
        itembtnc = types.KeyboardButton('Exit programme.')
        markup.row(itembtna)
        markup.row(itembtnb)
        markup.row(itembtnc)  
        
        bot.register_next_step_handler(msg, detailsConfirmation)


@bot.message_handler(commands=['setdate'])
def calendar(m):
    calendar, step = DetailedTelegramCalendar().build()
    bot.send_message(m.chat.id,
                    f"Select {LSTEP[step]}",
                    reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    chat_id = c.message.chat.id
    user = user_dict[chat_id]
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        input_date = result # type(result) = date
        today = date.today()
        delta_parts = str(result-today).split(' ')
        processed_date = '-'.join(str(input_date).split('-')[::-1])
        if len(delta_parts) == 1 or int(delta_parts[0]) > 0:
            user.date_delta = int(delta_parts[0])
            user.date = processed_date
            if user.date_delta <= 14:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                itembtna = types.KeyboardButton('Yes')
                itembtnb = types.KeyboardButton('No')
                itembtnc = types.KeyboardButton('Exit')
                markup.row(itembtna)
                markup.row(itembtnb)
                markup.row(itembtnc)                
                msg = bot.send_message(chat_id, f"Confirm date for {processed_date}?", reply_markup=markup)
                bot.register_next_step_handler(msg, dateConfirmation)
            else:
                 bot.send_message(chat_id, f"{processed_date} is too far. Please enter a date within 2 weeks from now.\n\nClick on another date or type /setdate to reset calendar.")
        else:
            bot.send_message(chat_id, f"{processed_date} is an invalid date. Please enter a date that has not passed.\n\nClick on another date or type /setdate to reset calendar.")


def dateConfirmation(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]

    if message.text == 'Exit':
        msg = bot.reply_to(message, 'Sucessfully ended. Type in anything to restart.')
        bot.register_next_step_handler(msg, send_welcome)
        user.driver.quit()
    elif message.text == 'No':
        bot.reply_to(message, "Please enter the date again. \n\nClick on /setdate or type /setdate to reset calendar.")
    elif message.text == 'Yes':
        bot.send_message(chat_id, "Please wait a moment while I confirm the date...")
        
        driver = user.driver
        time.sleep(1)
        frameBottom = driver.find_element_by_xpath('//*[@id="frameBottom"]')
        driver.switch_to.frame(frameBottom)
        bookingOverlay = driver.find_element_by_xpath('//*[@id="frameContent"]')
        driver.switch_to.frame(bookingOverlay)
        time.sleep(1)

        # set Date
        dateToBook = getDate(user.date_delta) # parameters is the number of days in the future
        dateToBookPath = '//*[@title="' + dateToBook + '"]'
        openDate = driver.find_element_by_xpath('//*[@id="DateBookingFrom_c1_textDate"]').click()
        try:
            selDate = driver.find_element_by_xpath(dateToBookPath).click()
        except NoSuchElementException:
            nextArrow = driver.find_element_by_xpath('//*[@id="__calendar_nextArrow"]').click()
            selDate = driver.find_element_by_xpath(dateToBookPath).click()

        bot.reply_to(message, f"Date confirmed! You selected {user.date}, {user.date_delta} days from now.")
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtna = types.KeyboardButton('School of Accountancy')
        itembtnb = types.KeyboardButton('School of Computing and Information Systems')
        itembtnc = types.KeyboardButton('School of Economics/Social Sciences')
        markup.row(itembtna)
        markup.row(itembtnb)
        markup.row(itembtnc)
        msg = bot.send_message(chat_id, "Choose one building to book facility in:", reply_markup=markup)
        
        bot.register_next_step_handler(msg, getBuilding)
    else:
        msg = bot.reply_to(message, "Invalid input.")
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtna = types.KeyboardButton('Yes')
        itembtnb = types.KeyboardButton('No')
        itembtnc = types.KeyboardButton('Exit')
        markup.row(itembtna)
        markup.row(itembtnb)
        markup.row(itembtnc)  
        
        bot.register_next_step_handler(msg, dateConfirmation)


def getBuilding(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    
    if message.text not in ['School of Accountancy', 'School of Computing and Information Systems', 'School of Economics/Social Sciences']:
        msg = bot.reply_to(message, "Invalid input, choose one of the following building types. ")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtna = types.KeyboardButton('School of Accountancy')
        itembtnb = types.KeyboardButton('School of Computing and Information Systems')
        itembtnc = types.KeyboardButton('School of Economics/Social Sciences')
        markup.row(itembtna)
        markup.row(itembtnb)
        markup.row(itembtnc)

        bot.register_next_step_handler(msg, getBuilding)
    else:
        user.buildingType = message.text

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtna = types.KeyboardButton('Yes, confirm.')
        itembtnb = types.KeyboardButton('No, re-enter details.')
        itembtnc = types.KeyboardButton('Exit.')
        markup.row(itembtna)
        markup.row(itembtnb)
        markup.row(itembtnc)

        msg = bot.reply_to(message, f"Confirm building: {user.buildingType}?", reply_markup=markup)

        bot.register_next_step_handler(msg, buildingConfirmation)


def buildingConfirmation(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]

    if message.text == 'Yes, confirm.':
        bot.send_message(chat_id, "Loading, please wait a moment...")

        driver = user.driver
        openBuilding = driver.find_element_by_xpath('//*[@id="DropMultiBuildingList_c1_textItem"]').click()
        buildingTypeMap = {
            "School of Accountancy": '//*[@id="6"]',
            "School of Computing and Information Systems": '//*[@id="7"]',
            "School of Economics/Social Sciences": '//*[@id="8"]'
        }
        buildingCheckbox = driver.find_element_by_xpath(buildingTypeMap[user.buildingType]).click()
        buildingConfirmation = driver.find_element_by_xpath('//*[@id="DropMultiBuildingList_c1_panelTreeView"]/input[1]').click()
        
        time.sleep(1)
        # facility type details
        openType = driver.find_element_by_xpath('//*[@id="DropMultiFacilityTypeList_c1_textItem"]').click()
        facilityTypeMap = {"CR": '/html/body/div[2]/form/span[1]/span/span/div/div/div/div/div/span/span/span/div/div/div[1]/div[8]/div/div/span/div/table/tbody/tr/td/table/tbody/tr/td/div/div/div/label[1]/input',
                            "SR": '/html/body/div[2]/form/span[1]/span/span/div/div/div/div/div/span/span/span/div/div/div[1]/div[8]/div/div/span/div/table/tbody/tr/td/table/tbody/tr/td/div/div/div/label[3]/input',
                            "GSR": '/html/body/div[2]/form/span[1]/span/span/div/div/div/div/div/span/span/span/div/div/div[1]/div[8]/div/div/span/div/table/tbody/tr/td/table/tbody/tr/td/div/div/div/label[2]/input'
                            }
        typeGSR = driver.find_element_by_xpath(facilityTypeMap["GSR"]).click()
        typeConfirmation = driver.find_element_by_xpath('//*[@id="DropMultiFacilityTypeList_c1_panelTreeView"]/input[1]').click()

        time.sleep(2)
        # search Availability
        searchAvailability = driver.find_element_by_xpath('//*[@id="CheckAvailability"]/span').click()
        # randomly click a square # 431
        try:
            clickTime = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="dps"]/div[3]/div[3]/div/div[2]/div[431]'))).click()
            time.sleep(2)
            makeBooking = driver.find_element_by_xpath('//*[@id="btnMakeBooking"]').click()
            bot.reply_to(message, f"Building confirmed! You selected {user.buildingType}.")
            bot.send_message(chat_id, "To select time slot, click /time or type /time.")
        except ElementClickInterceptedException:
            bot.send_message(chat_id, "Oops! There is no available GSR slot for this date.")
            bot.send_message(chat_id, "Logging out...")      
            driver.quit()
            bot.send_message(chat_id, f"To book a facility again, please type /book. Sorry! You will have to re-login again :(")
            
    elif message.text == 'No, re-enter details.':
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtna = types.KeyboardButton('School of Accountancy')
        itembtnb = types.KeyboardButton('School of Computing and Information Systems')
        itembtnc = types.KeyboardButton('School of Economics/Social Sciences')
        markup.row(itembtna)
        markup.row(itembtnb)
        markup.row(itembtnc)
        user.buildingType = message.text

        msg = bot.send_message(chat_id, "Please re-enter the building you wish to book facility in.", reply_markup=markup)
        bot.register_next_step_handler(msg, getBuilding)

    elif message.text == 'Exit.':
        msg = bot.reply_to(message, 'Sucessfully ended. Type in anything to restart.')
        bot.register_next_step_handler(msg, send_welcome)

    else:
        msg = bot.reply_to(message, "Invalid input.")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtna = types.KeyboardButton('Yes, confirm.')
        itembtnb = types.KeyboardButton('No, re-enter details.')
        itembtnc = types.KeyboardButton('Exit.')
        markup.row(itembtna)
        markup.row(itembtnb)
        markup.row(itembtnc)

        bot.register_next_step_handler(msg, buildingConfirmation)


def displayTime(chat_id, date_delta, desc='start'):
    from datetime import date, time, datetime, timedelta
    day_of_week = (date.today() + timedelta(int(date_delta))).weekday()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    
    m = ' AM'
    hour = 9
    if day_of_week < 5:
        for i in range(9, 22):
            if hour == 13:
                hour = 1
            hour_f = f"{hour}:"
            if i >= 12:
                m = ' PM'
            itembtna = types.KeyboardButton(hour_f+'00:00'+m)
            itembtnb = types.KeyboardButton(hour_f+'30:00'+m)
            markup.row(itembtna, itembtnb)
            hour += 1
    else:
        for i in range(9, 17):
            if hour == 13:
                hour = 1
            hour_f = f"{hour}:"
            if i >= 12:
                m = ' PM'
            itembtna = types.KeyboardButton(hour_f+'00:00'+m)
            itembtnb = types.KeyboardButton(hour_f+'30:00'+m)
            markup.row(itembtna, itembtnb)
            hour += 1
                    
    msg = bot.send_message(chat_id, f"Select {desc} time: ", reply_markup=markup)
    return msg


@bot.message_handler(commands=['time'])
def startTime(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]

    msg = displayTime(chat_id, user.date_delta, desc='start')
    bot.register_next_step_handler(msg, endTime)


def endTime(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]

    if message.text[-7:-3] != "0:00" or len(message.text) < 10:
        bot.reply_to(message, "Invalid input. Please select a start time.")
        msg = displayTime(chat_id, user.date_delta, desc='start')
        bot.register_next_step_handler(msg, endTime)
    else:
        user.startTime = message.text

        msg = displayTime(chat_id, user.date_delta, desc='end')
        bot.register_next_step_handler(msg, timeslotProcessing)


def isValidTime(ts, te):
    ts_parts = ts.split(":")
    ts_end = ts_parts[2][-2:]
    ts_hr = int(ts_parts[0])
    ts_min = int(ts_parts[1])
    if ts_end == "PM" and ts_hr != 12:
        ts_hr += 12
    
    te_parts = te.split(":")
    te_end = te_parts[2][-2:]
    te_hr = int(te_parts[0])
    te_min = int(te_parts[1])
    if te_end == "PM" and te_hr != 12:
        te_hr += 12

    if ts_hr > te_hr:
        return False
    if ts_hr == te_hr:
        if ts_min >= te_min:
            return False
        else:
            return True
    return True


def timeslotProcessing(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]

    if message.text[-7:-3] != "0:00" or len(message.text) < 10:
        bot.reply_to(message, "Invalid input. Please select an end time.")
        msg = displayTime(chat_id, user.date_delta, desc='end')
        bot.register_next_step_handler(msg, timeslotProcessing)
    else:
        user.endTime = message.text
        if (isValidTime(user.startTime, user.endTime)):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            itembtna = types.KeyboardButton('Yes')
            itembtnb = types.KeyboardButton('No')
            itembtnc = types.KeyboardButton('Exit')
            markup.row(itembtna)
            markup.row(itembtnb)
            markup.row(itembtnc)                
            msg = bot.send_message(chat_id, f"Confirm timeslot:\n{user.date}, {user.startTime} to {user.endTime}?", reply_markup=markup)
            bot.register_next_step_handler(msg, timeslotConfirmation)
        else:
            bot.send_message(chat_id, f"Start time must be before end time. Please enter the timeslot again. \n\nClick on /time or type /time to reset time.")



        
def timeslotConfirmation(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if message.text == 'Exit':
        msg = bot.reply_to(message, 'Sucessfully ended. Type in anything to restart.')
        bot.register_next_step_handler(msg, send_welcome)
    elif message.text == 'No':
        bot.reply_to(message, "Please enter the timeslot again. \n\nClick on /time or type /time to reset time.")
    elif message.text == 'Yes':
        bot.send_message(chat_id, "Please wait a moment, confirming timeslot...")
        driver = user.driver
        # switch to frame
        frameBookingDetails = driver.find_element_by_xpath('//*[@id="frameBookingDetails"]')
        driver.switch_to.frame(frameBookingDetails)
        # fill in purpose textbox
        purpose = driver.find_element_by_xpath('//*[@id="bookingFormControl1_TextboxPurpose_c1"]').send_keys('Project meeting')
        # select type acad/adhoc
        useTypeDropdown = driver.find_element_by_xpath('//*[@id="bookingFormControl1_DropDownUsageType_c1"]').click()
        optionAcad = '//*[@id="bookingFormControl1_DropDownUsageType_c1"]/option[2]'
        optionAdHoc = '//*[@id="bookingFormControl1_DropDownUsageType_c1"]/option[3]'
        selectType = driver.find_element_by_xpath(optionAdHoc).click()
        # select booking usage dropdown
        bookingUsageDropdown = driver.find_element_by_xpath('//*[@id="bookingFormControl1_DropDownSpaceBookingUsage_c1"]').click()
        optionMeeting = '//*[@id="bookingFormControl1_DropDownSpaceBookingUsage_c1"]/option[3]'
        selectUsage = driver.find_element_by_xpath(optionMeeting).click()
        # select time
        selectFromDropdown = Select(driver.find_element_by_xpath('//*[@id="bookingFormControl1_DropDownStartTime_c1"]'))
        selTimeFrom = selectFromDropdown.select_by_value(getDatetime(user.startTime, user.date_delta))
        time.sleep(2)
        selectToDropdown = Select(driver.find_element_by_xpath('//*[@id="bookingFormControl1_DropDownEndTime_c1"]'))
        selectTimeTo = selectToDropdown.select_by_value(getDatetime(user.endTime, user.date_delta))


        bot.reply_to(message, f"Timeslot confirmed! You selected {user.date}, {user.startTime} to {user.endTime}")
        # bot.send_message(chat_id, f"Username: {user.username}\n\nPassword: {user.password_hidden}\n\nDate selected: {user.date}, {user.date_delta} days from now.\n\nBuilding selected: {user.buildingType}\n\nTimeslot: {user.startTime} to {user.endTime}")
        bot.send_message(chat_id, f"To continue, please add at least one co-booker. To do so, click /add or type /add.")
        # bot.register_next_step_handler(msg, getBuilding)
    else:
        msg = bot.reply_to(message, "Invalid input.")
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtna = types.KeyboardButton('Yes')
        itembtnb = types.KeyboardButton('No')
        itembtnc = types.KeyboardButton('Exit')
        markup.row(itembtna)
        markup.row(itembtnb)
        markup.row(itembtnc)  
        
        bot.register_next_step_handler(msg, timeslotConfirmation)
    


def displayBookers(co_bookers):
    if len(co_bookers) == 0:
        return "There are currently no co-bookers added."
    else:
        res_str = ''
        for i in range(len(co_bookers)):
            res_str += f"{i+1}. {co_bookers[i]}\n"
        return res_str


@bot.message_handler(commands=['add'])
def addCoBooker(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.co_bookers = []

    msg = bot.send_message(chat_id, "Please type in the \n1. Full name (as stated on eLearn, e.g. John Doe), or\n2. Full email (e.g. john.doe.2020@sis.smu.edu.sg)\nof a co-booker you wish to add.")
    bot.register_next_step_handler(msg, processCoBooker)


def processCoBooker(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    co_booker = message.text
    user.co_bookers.append(co_booker)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    itembtna = types.KeyboardButton('Yes')
    itembtnb = types.KeyboardButton('No')
    markup.row(itembtna)
    markup.row(itembtnb)
    msg = bot.reply_to(message, f"Confirm co-booker: {co_booker}?\n\nDouble check name OR email.", reply_markup=markup)

    bot.register_next_step_handler(msg, confirmCoBooker)


def confirmCoBooker(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]

    if message.text == 'No':
        user.co_bookers.pop()

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtna = types.KeyboardButton('Yes')
        itembtnb = types.KeyboardButton('No')
        markup.row(itembtna)
        markup.row(itembtnb)
        if len(user.co_bookers) != 0:
            msg = bot.send_message(chat_id, f"People you have added so far:\n\n{displayBookers(user.co_bookers)}\n\nDo you want to add another co-booker?", reply_markup=markup)
        else:
            msg = bot.send_message(chat_id, f"{displayBookers(user.co_bookers)}\n\nDo you want to add another co-booker?", reply_markup=markup)

        bot.register_next_step_handler(msg, addNewBooker)

    elif message.text == 'Yes':
        bot.reply_to(message, f"Co-booker confirmed: {user.co_bookers[-1]}.")
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtna = types.KeyboardButton('Yes')
        itembtnb = types.KeyboardButton('No')
        markup.row(itembtna)
        markup.row(itembtnb)
        if len(user.co_bookers) != 0:
            msg = bot.send_message(chat_id, f"People you have added so far:\n\n{displayBookers(user.co_bookers)}\n\nDo you want to add another co-booker?", reply_markup=markup)
        else:
            msg = bot.send_message(chat_id, f"{displayBookers(user.co_bookers)}\n\nDo you want to add another co-booker?", reply_markup=markup)

        bot.register_next_step_handler(msg, addNewBooker)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtna = types.KeyboardButton('Yes')
        itembtnb = types.KeyboardButton('No')
        markup.row(itembtna)
        markup.row(itembtnb)
        msg = bot.reply_to(message, "Invalid input.", reply_markup=markup)
        bot.register_next_step_handler(msg, confirmCoBooker)


def addNewBooker(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]

    if message.text == 'Yes':
        msg = bot.reply_to(message, "Please type in the \n1. Full name (as stated on eLearn, e.g. John Doe), or\n2. Full email (e.g. john.doe.2020@sis.smu.edu.sg)\nof another co-booker you wish to add.")
        bot.register_next_step_handler(msg, processCoBooker)

    elif message.text == 'No':
        if len(user.co_bookers) != 0:
            bot.send_message(chat_id, "Please wait a moment while I confirm the details...")
            driver = user.driver
            book(driver, user.co_bookers)
            # agree to terms
            agreeBtn = driver.find_element_by_xpath('//*[@id="bookingFormControl1_TermsAndConditionsCheckbox_c1"]').click()
            # confirmBtn = driver.find_element_by_xpath('//*[@id="panel_UIButton2"]').click()

            bot.reply_to(message, f"Here are the details:\n\nUsername: {user.username}\nPassword: {user.password_hidden}\nDate: {user.date}, {user.date_delta} days from now\nBuilding: {user.buildingType}.\nTimeslot: {user.startTime} to {user.endTime}\n\nCo-bookers:\n{displayBookers(user.co_bookers)}")
        else:
            bot.reply_to(message, "You have to add at least 1 co-booker. Type /add or click /add to continue.")
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtna = types.KeyboardButton('Yes')
        itembtnb = types.KeyboardButton('No')
        markup.row(itembtna)
        markup.row(itembtnb)
        msg = bot.reply_to(message, "Invalid input.", reply_markup=markup)       
        bot.register_next_step_handler(msg, addNewBooker)


### ---------- VAR DUMP ---------- ###

@bot.message_handler(commands=['dump']) # command /dump
def addCoBooker(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]

    bot.send_message(chat_id, "Var dump\n\n")

    bot.send_message(chat_id, f"Username: {user.username}\nType: {type(user.username)}")
    bot.send_message(chat_id, f"Password: {user.password}\nType: {type(user.password)}")
    bot.send_message(chat_id, f"Date delta: {user.date_delta}\nType: {type(user.date_delta)}")
    bot.send_message(chat_id, f"Building Type: {user.buildingType}\nType: {type(user.buildingType)}")
    bot.send_message(chat_id, f"Facility type: {user.facilityType}\nType: {type(user.facilityType)}")
    bot.send_message(chat_id, f"Start Time: {user.startTime}\nType: {type(user.startTime)}")
    bot.send_message(chat_id, f"End Time: {user.endTime}\nType: {type(user.endTime)}")
    bot.send_message(chat_id, f"Co-Bookers: \n{displayBookers(user.co_bookers)}Type: {type(user.co_bookers)}")



### ---------- END OF VAR DUMP ---------- ###

bot.polling()
