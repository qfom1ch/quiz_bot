from aiogram import Router
from aiogram.types import Message

router: Router = Router()


@router.message()
async def send_echo(message: Message):
    await message.answer(
        f'Извините, но я не понимаю команду {message.text}. '
        f'Пожалуйста, попробуйте еще раз или воспользуйтесь командой '
        f'/help для получения дополнительной информации о доступных командах')
