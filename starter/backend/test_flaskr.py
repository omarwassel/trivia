import os
import unittest
import json
import psycopg2
from sqlalchemy.dialects.postgresql import insert
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        # self.database_name = "trivia"
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}{}/{}".format('postgres:4795863251O@','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            
            # create all tables
            self.db.create_all()
        
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    """
    categories
    """
    def test_get_gategories(self):
        res=self.client().get(('/categories'))
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['categories']['1'],'Science')
        

    def test_get_gategory_questions_by_id(self):
        res=self.client().get(('/categories/1/questions'))
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['total_questions'],3)
        self.assertEqual(data['current_category'],'Science')
    
    def test_get_gategory_questions_by_id_not_found(self):
        res=self.client().get(('/categories/8/questions'))
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['success'],False)

    """
    questions
    """
    def test_get_questions(self): 
        res=self.client().get(('/questions?page=1'))
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['total_questions'])
    
    def test_get_questions_404(self):
        res=self.client().get(('/questions?page=1000'))
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['success'],False)


    def test_delete_question(self):
        res=self.client().delete(('/questions/5'))
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['success'])

    def test_delete_question_by_id_not_found(self):
        res=self.client().delete(('/questions/1000'))
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['error'],404)
        self.assertFalse(data['success'])

    
    def test_create_question(self):
        res=self.client().post(('/questions'),json={'question':'What is OOP ?','answer':'object oriented programming','category':'Science','difficulty':3})
        data=json.loads(res.data)
        self.assertEquals(res.status_code,200)
        self.assertTrue(data['success'])
    
    def test_create_question_with_wrong_format(self):
        res=self.client().post(('/questions'),json={'quest':'What is OOP ?','answer':'object oriented programming','category':'Science','difficulty':3})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertFalse(data['success'])

    def test_search_for_questions(self):
        res=self.client().post(('/questions/search'),json={'searchTerm': 'title'})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['total_questions'])
        
    def test_search_for_questions_with_empty_term(self):
        res=self.client().post(('/questions/search'),json={'searchTerm': ''})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,404)
    
    """
    quiz

    """
    def test_get_quiz_question(self):
        res=self.client().post(('/quizzes') 
            ,json={'previous_questions': [], 'quiz_category': {'type': "Science", 'id': 1}})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertTrue(data['question'])

    def test_get_quiz_question_500_error(self):
        res=self.client().post(('/quizzes') ,json={'previous_questions': ['true'], 'quiz_category': {'type': "Geography", 'id': 5}})
        data=json.loads(res.data)
        self.assertEqual(res.status_code,500)
        self.assertFalse(data['success'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()