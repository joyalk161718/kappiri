from typing import Optional

from telegram import Message, Update, Bot, User
from telegram import MessageEntity
from telegram.ext import Filters, MessageHandler, run_async

from tg_bot import dispatcher
from tg_bot.modules.disable import DisableAbleCommandHandler, DisableAbleRegexHandler
from tg_bot.modules.sql import afk_sql as sql
from tg_bot.modules.users import get_user_id

AFK_GROUP = 7
AFK_REPLY_GROUP = 8


@run_async
def afk(bot: Bot, update: Update):
    args = update.effective_message.text.split(None, 1)
    if len(args) >= 2:
        reason = args[1]
    else:
        reason = ""

    sql.set_afk(update.effective_user.id, reason)
    update.effective_message.reply_text("{} ഇവിടെ ഇല്ലെന്ന് പറയാൻ പറഞ്ഞു... ".format(update.effective_user.first_name))


@run_async
def no_longer_afk(bot: Bot, update: Update):
    user = update.effective_user  # type: Optional[User]

    if not user:  # ignore channels
        return

    res = sql.rm_afk(user.id)
    if res:
        update.effective_message.reply_text("{} വന്നിട്ടുണ്ട് ആർക്കേലും എന്തേലും പറയാനുണ്ടേൽ ഇപ്പൊ പറഞ്ഞോ.... ഇനി അറിഞ്ഞില്ല കേട്ടില്ല പറയരുത്.....".format(update.effective_user.first_name))


@run_async
def reply_afk(bot: Bot, update: Update):
    message = update.effective_message  # type: Optional[Message]
    if message.entities and message.parse_entities([MessageEntity.TEXT_MENTION, MessageEntity.MENTION]):
        entities = message.parse_entities([MessageEntity.TEXT_MENTION, MessageEntity.MENTION])
        for ent in entities:
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
                fst_name = ent.user.first_name

            elif ent.type == MessageEntity.MENTION:
                user_id = get_user_id(message.text[ent.offset:ent.offset + ent.length])
                if not user_id:
                    # Should never happen, since for a user to become AFK they must have spoken. Maybe changed username?
                    return
                chat = bot.get_chat(user_id)
                fst_name = chat.first_name

            else:
                return

            if sql.is_afk(user_id):
                user = sql.check_afk_status(user_id)
                if not user.reason:
                    res = "{} ഇപ്പോൾ സ്ഥലത്തില്ല കാരണം !".format(fst_name)
                else:
                    res = "{} ഇപ്പോൾ സ്ഥലത്തില്ല.... കാരണം പറഞ്ഞിരിക്കുന്നത്.. :\n{}".format(fst_name, user.reason)
                message.reply_text(res)


__help__ = """
 - /afk <reason>: നിങ്ങൾ സ്ഥലത്തില്ല എന്നറിയിക്കാൻ...
 - brb <reason>: വല്യ മാറ്റം ഒന്നും ഇല്ല മേലെ പറഞ്ഞത് തന്നെ.....

AFK ഓൺ ആക്കി വെച്ചാൽ നിങ്ങളെ ആര് മെൻഷൻ ചെയ്താലും നിങ്ങ സ്ഥലത്തില്ലന്ന് പറയും......
"""

__mod_name__ = "കി.നീ.അ"

AFK_HANDLER = DisableAbleCommandHandler("afk", afk)
AFK_REGEX_HANDLER = DisableAbleRegexHandler("(?i)brb", afk, friendly="afk")
NO_AFK_HANDLER = MessageHandler(Filters.all & Filters.group, no_longer_afk)
AFK_REPLY_HANDLER = MessageHandler(Filters.entity(MessageEntity.MENTION) | Filters.entity(MessageEntity.TEXT_MENTION),
                                   reply_afk)

dispatcher.add_handler(AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REGEX_HANDLER, AFK_GROUP)
dispatcher.add_handler(NO_AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REPLY_HANDLER, AFK_REPLY_GROUP)
