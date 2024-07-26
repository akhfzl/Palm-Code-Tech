from flask_restful import Resource, reqparse
from flask import request, jsonify

import os, sys, json, csv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.main import *
from data.main import *

class ChatBotResponse(Resource):
    def post(self):
        # read dataframe
        df = read_csv('chatbot/data/appointments.csv')
        df = fitur_engineering(df)
        
        # receive input
        data = request.get_data()
        json_string = data.decode('utf-8')

        data = json.loads(json_string)
        message = data.get('message', {})
        content = message.get('content')
        id = message.get('id')

        # check pattern input
        input_pattern = information_extract(content)
       
        # if there're not pattern, the generate text is ussually text according to model pretrained
        if not input_pattern:
            response = GenerateResponse(content, is_time=False)
        
            return jsonify({
                "message": {
                    "id": id,
                    "content": response
                }
            })
        
        # if there're pattern, the generate text is according to logic conditional
        else:
            # check start booked is available ?
            date_selected = date_selection(input_pattern['start'])
            start_time_selected = time_selection(input_pattern['start'])
            end_time_selected = time_selection(input_pattern['end'])
            time_checking_start = patterns(input_pattern['start'])
            time_checking_end = patterns(input_pattern['end'])
            
            if not time_checking_start and not time_checking_end:
                return jsonify({
                    "message": {
                        "id": id,
                        "content": "Time format doesn't match"
                    }
                })
            
            cond = check_range_zone(input_pattern, df)
                
            if cond:
                new_data = [input_pattern['name'], date_selected, start_time_selected, end_time_selected]
              
                with open('chatbot/data/appointments.csv', 'a', newline='\n') as file:
                    writer = csv.writer(file)
                    writer.writerow(new_data)

                return jsonify({
                    "message": {
                        "id": id,
                        "content": "Your slots already booked, and the schedule has saved in our system"
                    }
                })

            else:
                return jsonify({
                    "message": {
                        "id": id,
                        "content": "Your schedule for booked slots has been unavailable, select other schedule please"
                    }
                })
    
    def get(self):
        return {'halo': 'world'}
