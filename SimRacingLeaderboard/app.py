# app.py
from flask import Flask, render_template
import json

app = Flask(__name__)
app.jinja_env.globals.update(max=max)
app.jinja_env.globals.update(min=min)


def load_laptimes():
    with open('C:\\Users\\simra\\PycharmProjects\\SimRacingOS\\laptimes.json', 'r') as file:
        return json.load(file)


def format_laptime(milliseconds):
    seconds = milliseconds / 1000
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    # Always include minutes and ensure 2 digits for minutes and seconds
    return f"{minutes:01d}:{remaining_seconds:05.3f}"


# Register the custom filter
app.jinja_env.filters['format_laptime'] = format_laptime


def process_leaderboard_data(data):
    leaderboard = {}

    for user in data:
        for task in data[user]:
            if task not in leaderboard:
                leaderboard[task] = {
                    'best_laptime': {'value': float('inf'), 'user': None},
                    'best_splits': [],
                    'best_speeds': {'value': 0, 'user': None},
                    'best_brake': {'value': float('inf'), 'user': None, 'is_infinite': True},
                    'best_longest_time': {'value': 0, 'user': None},
                    'best_longest_distance': {'value': 0, 'user': None},
                    'best_highest_angle': {'value': 0, 'user': None},
                    'best_total_dist': {'value': 0, 'user': None},
                    'participants': [],
                    'all_runs': []
                }

    # Process data
    for user in data:
        for task in data[user]:
            if user not in leaderboard[task]['participants']:
                leaderboard[task]['participants'].append(user)

            for run in data[user][task]:
                # Store all runs with user information
                run_with_user = run.copy()
                run_with_user['user'] = user
                leaderboard[task]['all_runs'].append(run_with_user)

                if 'laptime' in run:
                    if run['laptime'] < leaderboard[task]['best_laptime']['value']:
                        leaderboard[task]['best_laptime'] = {
                            'value': run['laptime'],
                            'user': user
                        }

                if 'speeds' in run:
                    max_speed = max(run['speeds'])
                    if max_speed > leaderboard[task]['best_speeds']['value']:
                        leaderboard[task]['best_speeds'] = {
                            'value': max_speed,
                            'user': user
                        }

                if 'brake_distances' in run:
                    min_brake = min(run['brake_distances'])
                    if min_brake < leaderboard[task]['best_brake']['value']:
                        leaderboard[task]['best_brake'] = {
                            'value': min_brake,
                            'user': user,
                            'is_infinite': False
                        }

                # New logic for Übersteuern and Driften
                if task == "Übersteuern":
                    if run['longest_time'] > leaderboard[task]['best_longest_time']['value']:
                        leaderboard[task]['best_longest_time'] = {
                            'value': run['longest_time'],
                            'user': user
                        }

                    if run['longest_distance'] > leaderboard[task]['best_longest_distance']['value']:
                        leaderboard[task]['best_longest_distance'] = {
                            'value': run['longest_distance'],
                            'user': user
                        }

                    if run['highest_angle'] > leaderboard[task]['best_highest_angle']['value']:
                        leaderboard[task]['best_highest_angle'] = {
                            'value': run['highest_angle'],
                            'user': user
                        }

                if task == "Driften":
                    if run['laptime'] < leaderboard[task]['best_laptime']['value']:
                        leaderboard[task]['best_laptime'] = {
                            'value': run['laptime'],
                            'user': user
                        }

                    if run['longest_time'] > leaderboard[task]['best_longest_time']['value']:
                        leaderboard[task]['best_longest_time'] = {
                            'value': run['longest_time'],
                            'user': user
                        }

                    if run['longest_distance'] > leaderboard[task]['best_longest_distance']['value']:
                        leaderboard[task]['best_longest_distance'] = {
                            'value': run['longest_distance'],
                            'user': user
                        }

                    if run['highest_angle'] > leaderboard[task]['best_highest_angle']['value']:
                        leaderboard[task]['best_highest_angle'] = {
                            'value': run['highest_angle'],
                            'user': user
                        }

                    if run['total_dist'] > leaderboard[task]['best_total_dist']['value']:
                        leaderboard[task]['best_total_dist'] = {
                            'value': run['total_dist'],
                            'user': user
                        }

    # Sort all runs by laptime
    for task in leaderboard:
        leaderboard[task]['all_runs'].sort(key=lambda x: x['laptime'])

    return leaderboard


@app.route('/')
def index():
    data = load_laptimes()
    leaderboard = process_leaderboard_data(data)
    return render_template('leaderboard.html', leaderboard=leaderboard)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
