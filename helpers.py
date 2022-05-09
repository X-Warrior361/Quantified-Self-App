import matplotlib.pyplot as plt
from datetime import datetime, date
from matplotlib.dates import HourLocator, DateFormatter
from .models import Options


def calculate_days(day):            # Calculate the last logged date
    if day == 0:
        return 'Today'
    elif day == 1:
        return 'Yesterday'
    elif day < 7:
        return '{} days ago'.format(day)
    elif day < 14:
        return 'A Week ago'
    elif day < 30:
        return '{} weeks ago'.format(14//7)
    elif day < 60:
        return 'A month ago'
    elif day < 365:
        return '{} months ago'.format(day//30)
    else:
        return 'A year ago'


def create_graph(trackers, logs, options):
    if trackers.type == 'num':                  # Creates scatter graph
        x_axis, y_axis = [], []
        week_x_axis, week_y_axis = [], []
        month_x_axis, month_y_axis = [], []
        year_x_axis, year_y_axis = [], []

        for log in logs:
            day = log.time_stamp.date()
            x_axis.append(datetime.strptime(str(day), '%Y-%m-%d').strftime('%d-%m-%y'))
            y_axis.append(log.value_num)

            temp = date.today() - day
            if temp.days < 7:
                week_x_axis.append(datetime.strptime(str(day), '%Y-%m-%d').strftime('%d-%m-%y'))
                week_y_axis.append(log.value_num)
            if temp.days < 30:
                month_x_axis.append(datetime.strptime(str(day), '%Y-%m-%d').strftime('%d-%m-%y'))
                month_y_axis.append(log.value_num)
            if temp.days < 365:
                year_x_axis.append(datetime.strptime(str(day), '%Y-%m-%d').strftime('%d-%m-%y'))
                year_y_axis.append(log.value_num)

        plt.switch_backend('agg')
        plt.figure(figsize=(8, 6), dpi=80)
        plt.xticks(rotation=45)
        plt.xlabel('Days')
        plt.ylabel('Values')
        plt.scatter(x_axis, y_axis)
        plt.savefig('Quantified_Self/static/img/image.png')

        plt.cla()
        plt.xlabel('Days')
        plt.ylabel('Values')
        if week_y_axis:
            plt.xticks(rotation=45)
            plt.scatter(week_x_axis, week_y_axis)
            plt.savefig('Quantified_Self/static/img/week.png')
        else:
            plt.tick_params(axis='x', labelbottom=False)
            plt.savefig('Quantified_Self/static/img/week.png')

        plt.cla()
        plt.xlabel('Days')
        plt.ylabel('Values')
        if month_y_axis:
            plt.tick_params(axis='x', labelbottom=True)
            plt.xticks(rotation=45)
            plt.scatter(month_x_axis, month_y_axis)
            plt.savefig('Quantified_Self/static/img/month.png')
        else:
            plt.tick_params(axis='x', labelbottom=False)
            plt.savefig('Quantified_Self/static/img/month.png')

        plt.cla()
        plt.xlabel('Days')
        plt.ylabel('Values')
        if year_y_axis:
            plt.tick_params(axis='x', labelbottom=True)
            plt.xticks(rotation=45)
            plt.scatter(month_x_axis, month_y_axis)
            plt.savefig('Quantified_Self/static/img/year.png')
        else:
            plt.tick_params(axis='x', labelbottom=False)
            plt.savefig('Quantified_Self/static/img/year.png')

    elif trackers.type == 'mcq':                        # Creates bar graph
        x_axis, week, month, year = {}, {}, {},  {}
        for opt in options:
            x_axis[opt.name.strip()] = 0
            week[opt.name.strip()] = 0
            month[opt.name.strip()] = 0
            year[opt.name.strip()] = 0

        for log in logs:
            x_axis[log.value_mcq] += 1
            temp = date.today() - log.time_stamp.date()
            if temp.days < 7:
                week[log.value_mcq] += 1
            if temp.days < 30:
                month[log.value_mcq] += 1
            if temp.days < 365:
                year[log.value_mcq] += 1

        plt.xlabel('Options')
        plt.ylabel('Values')
        plt.switch_backend('agg')
        plt.bar(x_axis.keys(), x_axis.values())
        plt.savefig('Quantified_Self/static/img/image.png')

        plt.clf()
        plt.bar(week.keys(), week.values())
        plt.savefig('Quantified_Self/static/img/week.png')

        plt.clf()
        plt.bar(month.keys(), month.values())
        plt.savefig('Quantified_Self/static/img/month.png')

        plt.clf()
        plt.bar(year.keys(), year.values())
        plt.savefig('Quantified_Self/static/img/year.png')

    elif trackers.type == 'time':                   # Creates scatter graph
        x_axis, y_axis = [], []
        week_x_axis, week_y_axis = [], []
        month_x_axis, month_y_axis = [], []
        year_x_axis, year_y_axis = [], []

        for log in logs:
            time = datetime.strptime(str(log.value_time), '%H:%M:%S')
            day = log.time_stamp.date()
            x_axis.append(datetime.strptime(str(day), '%Y-%m-%d').strftime('%d-%m-%y'))
            y_axis.append(time)

            temp = date.today() - day
            if temp.days < 7:
                week_x_axis.append(datetime.strptime(str(day), '%Y-%m-%d').strftime('%d-%m-%y'))
                week_y_axis.append(time)
            if temp.days < 30:
                month_x_axis.append(datetime.strptime(str(day), '%Y-%m-%d').strftime('%d-%m-%y'))
                month_y_axis.append(time)
            if temp.days < 365:
                year_x_axis.append(datetime.strptime(str(day), '%Y-%m-%d').strftime('%d-%m-%y'))
                year_y_axis.append(time)

        plt.xlabel('Date')
        plt.ylabel('Values')
        plt.switch_backend('agg')
        plt.figure(figsize=(8, 6), dpi=80)
        ax = plt.subplot()
        ax.yaxis.set_major_locator(HourLocator())
        ax.yaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        plt.xticks(rotation=45)
        ax.scatter(x_axis, y_axis)
        plt.savefig('Quantified_Self/static/img/image.png')

        plt.cla()
        plt.xlabel('Date')
        plt.ylabel('Values')
        if week_y_axis:
            ax = plt.subplot()
            ax.yaxis.set_major_locator(HourLocator())
            ax.yaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            plt.xticks(rotation=45)
            ax.scatter(week_x_axis, week_y_axis)
            plt.savefig('Quantified_Self/static/img/week.png')
        else:
            plt.tick_params(axis='x', labelbottom=False)
            plt.savefig('Quantified_Self/static/img/week.png')

        plt.cla()
        plt.xlabel('Date')
        plt.ylabel('Values')
        if month_y_axis:
            plt.tick_params(axis='x', labelbottom=True)
            plt.xticks(rotation=45)
            ax = plt.subplot()
            ax.yaxis.set_major_locator(HourLocator())
            ax.yaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            plt.xticks(rotation=45)
            ax.scatter(month_x_axis, month_y_axis)
            plt.savefig('Quantified_Self/static/img/month.png')
        else:
            plt.tick_params(axis='x', labelbottom=False)
            plt.savefig('Quantified_Self/static/img/month.png')

        plt.cla()
        plt.xlabel('Date')
        plt.ylabel('Values')
        if year_y_axis:
            plt.tick_params(axis='x', labelbottom=True)
            plt.xticks(rotation=45)
            ax = plt.subplot()
            ax.yaxis.set_major_locator(HourLocator())
            ax.yaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            plt.xticks(rotation=45)
            ax.scatter(year_x_axis, year_y_axis)
            plt.savefig('Quantified_Self/static/img/year.png')
        else:
            plt.tick_params(axis='x', labelbottom=False)
            plt.savefig('Quantified_Self/static/img/year.png')

    else:                       # Creates pie chart
        x_axis, week, month, year = {'No logs': 0}, {'No logs': 0}, {'No logs': 0},  {'No logs': 0}
        for opt in options:
            x_axis[opt.name] = 0
            week[opt.name] = 0
            month[opt.name] = 0
            year[opt.name] = 0

        for log in logs:
            if log.value_bool == 1:
                opt = options[0].name
            else:
                opt = options[1].name

            x_axis[opt] += 1
            temp = date.today() - log.time_stamp.date()
            if temp.days < 7:
                week[opt] += 1
            else:
                week['No logs'] = 1
            if temp.days < 30:
                month[opt] += 1
            else:
                month['No logs'] = 1
            if temp.days < 365:
                year[opt] += 1
            else:
                month['No logs'] = 1

        plt.switch_backend('agg')
        x_axis = dict_filter(x_axis)
        plt.pie(x_axis.values(), labels=x_axis.keys(), autopct='%1.2f%%')
        plt.savefig('Quantified_Self/static/img/image.png')

        plt.clf()
        week = dict_filter(week)
        plt.pie(week.values(), labels=week.keys(), autopct='%1.2f%%')
        plt.savefig('Quantified_Self/static/img/week.png')

        plt.clf()
        month = dict_filter(month)
        plt.pie(month.values(), labels=month.keys(), autopct='%1.2f%%')
        plt.savefig('Quantified_Self/static/img/month.png')

        plt.clf()
        year = dict_filter(year)
        plt.pie(year.values(), labels=year.keys(), autopct='%1.2f%%')
        plt.savefig('Quantified_Self/static/img/year.png')


def dict_filter(data):                  # Excludes labels with values = 0
    return {k:v for k, v in data.items() if (v > 0 and k!='No logs') or (k=='No Logs' and v>1)}


def get_value(log):
    if log.value_num:
        return log.value_num
    if log.value_mcq:
        return log.value_mcq
    if log.value_time:
        return log.value_time
    if log.value_bool:
        opt = Options.query.filter_by(tracker_id=log.tracker_id).all()
        return opt[0].name
    else:
        opt = Options.query.filter_by(tracker_id=log.tracker_id).all()
        return opt[1].name
