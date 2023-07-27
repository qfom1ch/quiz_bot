from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database.models as models
from database.session import session
from quiz_bot.lexicon import FOR_RESULTS


class Player:

    def __init__(self, tg_id):
        self.player_id = tg_id

    def add_answer(self, answer):
        """ Добавить ответ игрока в таблицу ответов всех игроков"""
        player_q_id = self.get_q_id()
        answer_q_id = session.query(models.QuestionVariable).filter_by(
            variable=answer).with_entities(
            models.QuestionVariable.q_id).all()
        answer_q_id = answer_q_id[0][0]

        if player_q_id == 1 or player_q_id == answer_q_id:
            answer_choice_id = session.query(
                models.QuestionVariable).filter_by(variable=answer).first()
            answer_choice_id = answer_choice_id.id

            answer = models.PlayerAnswer(player_id=self.player_id,
                                         answer_id=answer_choice_id,
                                         q_id=player_q_id)
            session.add(answer)
            session.commit()
            return True
        return False

    def all_answers(self):
        """ Получение всех ответов игрока """
        player_answers = session.query(models.PlayerAnswer).filter_by(
            player_id=self.player_id).all()
        player_answers = [player_answer.answer.variable for player_answer in
                          player_answers]
        return player_answers

    def get_q_id(self, add=False):
        """ Получение айди вопроса, на котором остановился игрок """

        player_q_id = session.query(models.Player).with_entities(
            models.Player.current_q_id).filter_by(
            tg_id=self.player_id).all()
        player_q_id = player_q_id[0][0]

        if add:
            player_q_id += 1
            session.query(models.Player).filter_by(
                tg_id=self.player_id).update({'current_q_id': player_q_id})
            session.commit()
        return player_q_id


class Game:

    @staticmethod
    def check_player(id):
        """ Проверка существования игрока """
        player = session.query(models.Player).filter_by(tg_id=id).all()
        if not player:
            return False
        return True

    @staticmethod
    def create_player(id, name=None):
        """ Создание игрока """
        if name != None:
            new_player = models.Player(tg_id=id, name=name)
        else:
            new_player = models.Player(tg_id=id)
        session.add(new_player)
        session.commit()

    @staticmethod
    def set_finish_status(id, is_finished=True):
        """ Установка игроку значение поля finished """
        session.query(models.Player).filter_by(tg_id=id).update(
            {'is_finished': is_finished})
        session.commit()

    def restart_player(self, id):
        """ Рестарт игрока """
        player_answers = session.query(models.PlayerAnswer).filter_by(
            player_id=id).all()
        for answer in player_answers:
            session.delete(answer)
        self.set_finish_status(id, False)
        session.query(models.Player).filter_by(tg_id=id).update(
            {'current_q_id': 1})
        session.commit()


class Quiz(Game):

    @staticmethod
    def get_question(q_id):
        """ Получение текста текущего вопроса """
        question = session.query(models.Question).filter_by(id=q_id).all()
        return question[0].question

    @staticmethod
    def get_question_variables(q_id):
        """ Получение вариантов ответа для текущего вопроса """
        variables = session.query(models.QuestionVariable).filter_by(
            q_id=q_id).all()
        variables = [variable.variable for variable in variables]
        return variables

    @staticmethod
    def get_questions_count():
        """ Получение общего числа всех вопросов """
        questions = session.query(models.Question).all()
        return len(questions)

    @staticmethod
    def get_right_answers():
        """ Получение всех правильных ответов викторины """
        right_answers = session.query(models.RightAnswer).all()
        return [right_answer.right_answer for right_answer in right_answers]

    def get_quiz_results(self, answs):
        """ Получение процента правильных ответов и соответствующего текста """
        right_answers = self.get_right_answers()
        correct_answers = len(right_answers) - len(
            list(set(right_answers) - set(answs)))
        percent = (correct_answers / len(right_answers)) * 100

        if percent >= 90:
            text_result = FOR_RESULTS[0]
        elif percent >= 70:
            text_result = FOR_RESULTS[1]
        elif percent >= 50:
            text_result = FOR_RESULTS[2]
        else:
            text_result = FOR_RESULTS[3]

        return (percent, text_result, correct_answers, len(right_answers))

    def make_keyboard(self, question_id):
        """ Функция генерации клавиатуры для ответа пользователю """
        buttons = []
        for variable in self.get_question_variables(question_id):
            button = [{
                'text': variable,
                'callback_data': variable
            }]
            buttons.append(button)

        inline_keyboard = {'inline_keyboard': buttons}
        return inline_keyboard

    def create_buttons(self, question_id):
        keyboard = self.make_keyboard(question_id)
        kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
        for button in keyboard['inline_keyboard']:
            kb_builder.row(types.InlineKeyboardButton(
                text=button[0]['text'],
                callback_data=button[0]['callback_data']))
        return kb_builder.as_markup()

    @staticmethod
    def result_answer(result_list):
        """ Функция формирования текста результатов для ответа пользователю """
        percent, text_result, correct_answers, right_answers = result_list
        text = [
            '<i>Тест окончен.</i>',
            f'Процент правильных ответов: <b>{percent}%</b>',
            f'Это {correct_answers}/{right_answers} правильных ответов!'
            f'\n<strong>{text_result}</strong>',
        ]
        return '\n'.join(text)
