from flask_restful import Resource
from flask import request
from mysql.connector import Error
from database.db import get_db_connection
import logging

class FeedbackService(Resource):

    def post(self):
        try:
            data = request.get_json();
            if not data or 'feedback' not in data:
                return {'message': 'Missing required field'}, 400
            
            feedback = data['feedback'];
            email = data['email'];

            conn = get_db_connection();
            cursor = conn.cursor();
            cursor.execute("INSERT INTO feedback (feedback, email) VALUES (%s, %s)", (feedback, email));
            conn.commit();
            return {'message': 'Feedback submitted successfully'}, 201
        except Error as e:
            logging.error("Error submitting feedback: %s", e)
            return {'message': 'Error submitting feedback'}, 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def get(self):
        try:
            conn = get_db_connection();
            cursor = conn.cursor(dictionary=True);
            cursor.execute("SELECT * FROM feedback");
            feedback_records = cursor.fetchall();

            for record in feedback_records:
                if 'created_at' in record:
                    record['created_at'] = record['created_at'].isoformat()

            return {'feedback': feedback_records}, 200
        except Error as e:
            logging.error("Error fetching feedback: %s", e)
            return {'message': 'Error fetching feedback'}, 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
