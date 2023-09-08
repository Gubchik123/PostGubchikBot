from aiogram.types import CallbackQuery

from loader import bot, dp, _
from utils.db.crud.user import get_user_by_
from keyboards.inline.menu import get_back_to_menu_keyboard
from data.config import CURRENCY_SYMBOL, DEFAULT_REFERRAL_BONUS


@dp.callback_query_handler(text="referrals")
async def show_referrals(query: CallbackQuery) -> None:
    """Shows referrals info."""
    user = get_user_by_(query.from_user.id)
    bot_ = await bot.get_me()
    await query.message.edit_text(
        text=_(
            "👥 <b>Referral statistics</b>\n\n"
            "You balance: <b>{balance} {currency_symbol}</b>\n"
            "Referrals: <b>{referrals}</b>\n\n"
            "Your referral link:\n<code>{referral_link}</code>\n\n"
            "Invite your friends to the bot"
            "and get <b>{referral_bonus} {currency_symbol}</b> for each referral."
        ).format(
            balance=user.balance,
            currency_symbol=CURRENCY_SYMBOL,
            referrals=user.referrals,
            referral_link=f"https://t.me/{bot_.username}?start={user.chat_id}",
            referral_bonus=DEFAULT_REFERRAL_BONUS,
        ),
        reply_markup=get_back_to_menu_keyboard(),
    )
