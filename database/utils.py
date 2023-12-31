from sqlalchemy_utils.functions import database_exists

import quiz_bot.lexicon as lexicon
from database.models import Base, Question, QuestionVariable, RightAnswer
from database.session import engine, session


def set_new_quiz():
    """ Функция обновления БД для новой викторины """
    session.query(RightAnswer).delete()
    session.query(Question).delete()
    session.query(QuestionVariable).delete()
    session.commit()

    for id in range(1, len(lexicon.QUESTIONS) + 1):
        question_id = id - 1

        current_question = lexicon.QUESTIONS[question_id]['question']
        current_answer = lexicon.QUESTIONS[question_id]['answer']

        right_answer = RightAnswer(right_answer=current_answer)
        question = Question(question=current_question, answer_id=id)
        session.add(right_answer)
        session.add(question)
        session.commit()

        current_variables = lexicon.QUESTIONS[question_id]['variables']
        for var in current_variables:
            session.add(QuestionVariable(variable=var, q_id=id))
            session.commit()


def create_db(new_quiz=False):
    """ Создание БД """
    if not database_exists(engine.url):
        Base.metadata.create_all(engine)
        set_new_quiz()
    if new_quiz is True:
        set_new_quiz()
