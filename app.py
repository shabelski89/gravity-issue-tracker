"""
Telegram Bot to manual issue tracking
"""
__author__ = "Aleksandr Shabelsky"
__version__ = "0.9"
__email__ = "a.shabelsky@gmail.com"

import argparse
from gravity.bot import IssueBot
from gravity.models import IssueStatus, Statuses, Users, Messages, IssueStates
from gravity.tracker import DbOperator
from gravity.utills import *
from functools import wraps


def main(token: str, engine: str):
    bot = IssueBot(token=token, tracker=DbOperator(db=engine))
    bot.tracker.initialization()
    bot.tracker.create_all()
    if not bot.tracker.check_exists(Statuses, IssueStatus.Close.status_id):
        bot.tracker.add_all([
            Statuses(status_id=IssueStatus.Close.status_id, description=IssueStatus.Close.name),
            Statuses(status_id=IssueStatus.Open.status_id, description=IssueStatus.Open.name),
            Statuses(status_id=IssueStatus.Comment.status_id, description=IssueStatus.Comment.name)
        ])

    def catch_users_messages(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = args[0].from_user.id
            if not bot.tracker.check_exists(model=Users, arg=user_id):
                first_name = args[0].from_user.first_name,
                last_name = args[0].from_user.last_name,
                username = args[0].from_user.username
                bot.tracker.add(model=Users(user_id=user_id,
                                            first_name=first_name,
                                            last_name=last_name,
                                            username=username))
            message_id = args[0].id
            if not bot.tracker.check_exists(model=Messages, arg=message_id):
                message = args[0].text
                if args[0].reply_to_message:
                    reply_message_id = args[0].reply_to_message.id
                else:
                    reply_message_id = None
                bot.tracker.add(model=Messages(message_id=message_id,
                                               reply_message_id=reply_message_id,
                                               user_id=user_id,
                                               message=message))
            result = func(*args, **kwargs)
            return result

        return wrapper

    @bot.message_handler(commands=[IssueStatus.Open.command, IssueStatus.Close.command])
    @catch_users_messages
    def issue_handler(message):
        """Handling Open and Close command from message"""
        command = get_command_from_message(message.text)
        issue = get_issue_from_message(message.text)
        if command and issue:
            if command == IssueStatus.Open.command:
                bot.open_issue(msg=message, issue=issue)
            elif command == IssueStatus.Close.command:
                bot.close_issue(msg=message, issue=issue)
            else:
                bot.send_message(message.chat.id, f"Not accepted command - {command}!")
        else:
            bot.send_message(message.chat.id, f"ValueError in command - {command}!")

    @bot.message_handler(commands=['getWordcloud', 'getStat', 'getBar'])
    @catch_users_messages
    def informer(message):
        """Return image report of issues statistics, admins only"""
        # admins = bot.get_chat_administrators(message.chat.id)
        admins = [534905]
        if message.from_user.id in admins:
            command = get_command_from_message(message.text)
            if command:
                stat = None
                if command == 'getWordcloud':
                    stat = bot.get_wordcloud()
                elif command == 'getStat':
                    bot.send_message(message.chat.id, f"{command} - is under construction!")
                elif command == 'getBar':
                    bot.send_message(message.chat.id, f"{command} - is under construction!")
                if stat:
                    with open(stat, 'rb') as file:
                        bot.send_photo(message.chat.id, file)
            else:
                bot.send_message(message.chat.id, f"ValueError in command - {command}!")

    @bot.message_handler(content_types=['text'])
    @catch_users_messages
    def observer(message):
        """Handling message, which is comment issues"""
        if message.reply_to_message:

            message_chain = list(flatten(get_message_chain(message_id=message.id)))
            issues_message = get_issues()

            for elem in issues_message:
                issue_number, message_id = elem
                if message_id in message_chain:
                    bot.comment_issue(msg=message, issue=issue_number)
                    break

    def get_issues(status=IssueStatus.Open.status_id):
        """"""
        return bot.get_all(field=(IssueStates.issue_number, IssueStates.message_id),
                           filter=(IssueStates.status_id == status,))

    def get_message_chain(message_id):
        """"""
        result = []
        if message_id is None or message_id in result:
            return result
        message = bot.get_one(field=(Messages.message_id, Messages.reply_message_id),
                              filter=(Messages.message_id == message_id,))
        if message:
            p, c = message
            if c is not None:
                result.append(c)
                yield from get_message_chain(message_id=c)
        if result:
            yield result

    try:
        bot.infinity_polling()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    db_engine = "mysql+pymysql://sa:ads4Sashka@localhost/issue"
    bot_token = '1094375695:AAH53Kc0KmQY34pPVGyU8i0q7XbYNk0WCho'
    # command line argument parser with help message
    arg_parser = argparse.ArgumentParser(description="IssueBot", formatter_class=argparse.RawTextHelpFormatter)
    arg_parser.add_argument("-t", dest="token", required=True, help="Telegram Bot API Token")
    arg_parser.add_argument("-d", dest="database", required=True, help="SQLAlchemy DataBase Engine URL")
    arg_parser.add_argument("-a", dest="admins", required=False, help="IssueBot admins")
    args = arg_parser.parse_args()
    bot = IssueBot(token=args.token, tracker=DbOperator(db=args.database))
    # bot = IssueBot(token=bot_token, tracker=DbOperator(db=db_engine))

    main(token=args.token, engine=args.database)



