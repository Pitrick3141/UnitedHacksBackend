import requests
import os

base_url = 'https://api.pitrick.link/united-hacks/prompt'

prompt = input("please enter your new year resolution: ")

params = {'goal': prompt}

print('Generating your new year schedule...')

feedback = requests.get(base_url, params=params).json()

if not feedback['success']:
    print('Generate Failed: ' + feedback['message'])
    os.system('pause')
    exit()

generated_schedule = feedback['schedule']

for month in generated_schedule:
    print(month['month'], 'Activity: ', month['activity'])
    print(month['month'], 'Goal: ', month['goal'], '\n')

while True:
    month = int(input('please enter the month you want to elaborate (1-12): ')) - 1
    selected_month = generated_schedule[month]
    month_params = {'month': selected_month['month'],
                    'activity': selected_month['activity'],
                    'goal': selected_month['goal'],
                    'type': 'month'}
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    print('Generating your monthly schedule of {}...'.format(months[month]))
    generated_month_schedule = requests.get(base_url, params=month_params).json()
    if not feedback['success']:
        print('Generate Failed: ' + feedback['message'])
        os.system('pause')
        continue
    else:
        generated_month_schedule = generated_month_schedule['schedule']
    for week in generated_month_schedule:
        print('\nFor {} of {}, there are several activities and goals for you: '.format(week['week'], selected_month['month']))
        cnt = 1
        for activity in week['activity']:
            print("Activity #{}: {}".format(cnt, activity))
            cnt += 1
        cnt = 1
        for goal in week['goal']:
            print("Goal #{}: {}".format(cnt, goal))
            cnt += 1
