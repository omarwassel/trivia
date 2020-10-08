import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins.
  Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    def get_formatted_categories():
        cats = Category.query.all()
        if cats is None:
            abort(404)
        ans = {cat.id: cat.type for cat in cats}
        return ans

    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            return jsonify({'categories': get_formatted_categories()})
        except BaseException:
            abort(405)

    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            page = request.args.get('page', 1, type=int)

            questions = Question.query.all()
            formatted_questions = [q.format() for q in questions]

            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            page_questions = formatted_questions[start:end]

            if len(page_questions) == 0:
                abort(404)

            return jsonify({
                'questions': page_questions,
                'total_questions': len(formatted_questions),
                'categories': get_formatted_categories(),
                'current_category': 'null'
            })
        except BaseException:
            abort(404)

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:

            question = Question.query.get(id)
            question.delete()

            return jsonify({"success": True})

        except BaseException:
            abort(404)

    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            data = request.get_json()
            q = data['question']
            ans = data['answer']
            cat = data['category']
            dif = data['difficulty']
            question_info = Question(
                question=q, answer=ans, category=cat, difficulty=dif)
            print(question_info.format())
            if (q is None) or (ans is None) or (cat is None) or (dif is None):
                abort(422)
            else:
                question_info.insert()

            return jsonify({"success": True})
        except BaseException:
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def get_searrch_questions():
        try:

            data = request.get_json()
            searchTerm = data['searchTerm']

            if searchTerm == '':
                abort(404)

            s = '%' + str(searchTerm) + '%'
            questions = Question.query.filter(Question.question.ilike(s)).all()
            formatted_questions = [q.format() for q in questions]

            return jsonify({
                'questions': formatted_questions,
                'total_questions': len(formatted_questions),
                'current_category': 'null'
            })
        except BaseException:
            abort(404)

    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def get_category_questions(cat_id):
        try:
            questions = Question.query.filter(
                Question.category == cat_id).all()
            formatted_questions = [q.format() for q in questions]
            # if len(formatted_questions)==0:
            #     abort(404)

            cat = Category.query.get(cat_id)
            return jsonify({
                "questions": formatted_questions,
                'total_questions': len(formatted_questions),
                'current_category': cat.type
            })
        except BaseException:
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def creat_quiz():
        try:

            data = request.get_json()
            previous_questions = data['previous_questions']
            quiz_category = data['quiz_category']

            if quiz_category['type'] == 'click':
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()
            else:
                questions = Question.query.filter(
                    Question.category == quiz_category['id']) .filter(
                    Question.id.notin_(previous_questions)).all()

            formatted_questions = [q.format() for q in questions]
            ques = {}

            if len(formatted_questions) != 0:
                ran = random.randrange(0, len(formatted_questions), 1)
                ques = {
                    'question': formatted_questions[ran]
                }

            return jsonify(ques)
        except BaseException:
            abort(500)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'massage': 'Not Found'
        }), 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': 422,
            'massage': 'Unprocessable Entity'
        }), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'massage': 'Method Not Allowed'
        }), 405

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'massage': 'Bad request'
        }), 400

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'massage': 'INTERNAL SERVER ERROR'
        }), 500

    return app
