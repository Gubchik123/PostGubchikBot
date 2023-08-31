from aiogram import types

from loader import dp, _
from keyboards.inline.menu import get_menu_keyboard
from utils.db.user_crud import get_user_channels_by_


@dp.callback_query_handler(text="menu")
async def show_menu(query: types.CallbackQuery) -> None:
    """Shows menu."""
    user_channels = get_user_channels_by_(query.from_user.id)
    has_channels = bool(user_channels)
    if has_channels:
        channel_list_items = "\n".join(
            [f"<li>{channel.title}</li>" for channel in user_channels]
        )
        await query.message.edit_text(
            text=_(
                "Your channels:\n" "<ul>{channel_list_items}</ul>\n"
            ).format(channel_list_items=channel_list_items),
            reply_markup=get_menu_keyboard(has_channels=True),
        )
    else:
        await query.message.edit_text(
            text=_(
                "You currently have no channels.\n\n"
                "Use the button below or the /add command to add it."
            ),
            reply_markup=get_menu_keyboard(has_channels=False),
        )
