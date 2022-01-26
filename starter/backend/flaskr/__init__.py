import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, questions):
    #implement paginate
    page = request.args.get('page', 1, type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    formatted_questions = [question.format() for question in questions]
    current_page_questions = formatted_questions[start:end]
    return current_page_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"*" : {"origins": '*'}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,PATCH')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=["GET"])
  #@cross_origin
  def retrieves_categories():
    categories = Category.query.order_by(Category.id).all()
    formatted_categories = [category.format() for category in categories]

    if len(categories) == 0:
        abort(404)
    
    return jsonify({
        'success': True,
        'total_categories': len(categories),
        'categories': formatted_categories
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=["GET"])
  #@cross_origin
  def retrieves_questions():
    questions = Question.query.order_by(Question.id).all()
    formatted_questions = paginate(request, questions)
    categories = Category.query.order_by(Category.id).all()
    formatted_categories = [category.format() for category in categories]

    if len(formatted_questions) == 0:
        abort(404)
    
    if len(formatted_categories) == 0:
        abort(404)
    
    return jsonify({
        'success': True,
        'questions': formatted_questions,
        'totalQuestions': len(questions),
        'categories': formatted_categories,
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=["DELETE"])
  #@cross_origin
  def delete_specific_question(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()
    if question is None:
            abort(404)
    question.delete()

    return jsonify({
        'success': True,
        'deleted': question_id
    })
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=["POST"])
  #@cross_origin
  def create_question():
    
    try:
      body = request.get_json()
      question = body.get('question', None)
      answer = body.get('answer', None)
      category = body.get('category', None)
      difficulty = body.get('difficulty', None)
      question = Question(question, answer, category, difficulty)
      question.insert()
  
      return jsonify({
        'success': True
      })
    except:
      abort(400)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/result', methods=["POST"])
  #@cross_origin
  def search_question():
    try:
      body = request.get_json()
      search_term = body.get('searchTerm', None)
      result=Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
      formatted_questions = [question.format() for question in result]

      return jsonify({
          'success': True,
          'questions': formatted_questions,
          'totalQuestions': len(result),
          'curentCategory': None  
      })
    except:
      abort(400)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=["GET"])
  #@cross_origin
  def retrieves_category_questions(category_id):
    questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
    formatted_questions = paginate(request, questions)
    category = Category.query.filter(Category.id == category_id).one_or_none()
    if not category:
      abort(404)
    
    return jsonify({
        'success': True,
        'questions': formatted_questions,
        'totalQuestions': len(questions),
        'currentCategory': category_id
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=["POST"])
  #@cross_origin
  def retrieves_quiz():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    category = body.get('quiz_category', None)
    if category:
      try:
        category = Category.query.filter(Category.type == category).one_or_none()
        questions = Question.query.filter(Question.category == category.id).order_by(Question.id).all()
      except:
        abort(400)
    else:
      questions = Question.query.order_by(Question.id).all()
    total_questions=len(questions)
    if total_questions == 0:
      abort(422)
    random_question= questions[random.randrange(0,total_questions,1)]
    while random_question.id in previous_questions:
      if len(previous_questions) == total_questions:
        abort(422)
      else:
        random_question= questions[random.randrange(0,total_questions,1)]
    return jsonify({
      'success': True,
      'question': random_question.format()
    })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Not Found"
      }), 404

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "Bad Request"
      }), 400

  @app.errorhandler(422)
  def unprcessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "Unprocessable"
      }), 422
      
  return app

    