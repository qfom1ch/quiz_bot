from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from quiz_bot.lexicon import ALL_VARIABLES, LEXICON
from quiz_bot.services import Player, Quiz

router: Router = Router()


@router.message(CommandStart())
async def quiz_info(message: Message):
    """ Обработка запроса на команды """
    await message.answer(LEXICON['/start'])


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON['/help'])


@router.message(Command(commands='go'))
async def quiz_start(message: Message):
    """ Хендлер обработки запроса на старт викторины """
    current_game = Quiz()
    current_player = Player(message.chat.id)
    if not current_game.check_player(message.chat.id):
        current_game.create_player(message.chat.id)

    q_id = current_player.get_q_id()
    if q_id > current_game.get_questions_count():
        result = current_game.get_quiz_results(current_player.all_answers())
        await message.answer(current_game.result_answer(result))

    buttons = current_game.create_buttons(q_id)
    question = current_game.get_question(q_id)
    await message.answer(text=question,
                         reply_markup=buttons)


@router.message(Command(commands='restart'))
async def quiz_restart(message: Message):
    """  Хендлер обработки запроса на рестарт викторины """
    current_game = Quiz()
    current_player = Player(message.chat.id)

    if current_game.check_player(message.chat.id):
        if len(current_player.all_answers()) != \
                current_game.get_questions_count():
            text = 'Вы еще не завершили тестирование, чтобы начать сначала :)'
            await message.answer(text)
        else:
            current_game.restart_player(message.chat.id)
            q_id = current_player.get_q_id()
            buttons = current_game.create_buttons(q_id)
            await message.answer(
                text=current_game.get_question(q_id),
                reply_markup=buttons
            )
    else:
        text = '''Вы еще даже не проходили тест.,
            'Как я начну еще раз?',
            '<strong>Напишите мне лучше команду /go!</strong>'''
        await message.answer(text=text)


@router.callback_query(lambda call: call.data in ALL_VARIABLES)
async def user_answer(call: CallbackQuery):
    """ Хендлер обработки нажатой кнопки """
    current_game = Quiz()
    current_player = Player(call.from_user.id)

    if len(current_player.all_answers()) >= 0:
        if current_player.add_answer(call.data):
            text = '''Кстати, мы можем начать сначала, если хочешь :),
                    \nНажми ➡️ "/restart"!'''
            q_id = current_player.get_q_id(add=True)
            try:
                text = current_game.get_question(q_id)
            except IndexError:
                result = current_game.get_quiz_results(
                    current_player.all_answers())
                await call.message.answer(current_game.result_answer(result))
        else:
            q_id = current_player.get_q_id()
            text = '\n'.join([
                'Ая-яй! Вы уже ответили на этот вопрос :)',
                current_game.get_question(q_id)
            ])
        buttons = current_game.create_buttons(q_id)
        await call.message.answer(text=text, reply_markup=buttons)
