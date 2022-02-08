import telebot
import logging
from gravity.models import Issues, IssueStates, IssueStatus, Messages
from gravity.statistics import *

logger = telebot.logger
telebot.logger.setLevel(logging.ERROR)


class IssueBot(telebot.TeleBot):
    """
    Class bases on Telebot with special handling issues method.
    """
    def __init__(self, token, tracker):
        """"""
        super().__init__(token)
        self.tracker = tracker

    def get_one(self, **kwargs):
        """"""
        return self.tracker.get_one(**kwargs)

    def get_all(self, **kwargs):
        """"""
        return self.tracker.get_all(**kwargs)

    def open_issue(self, msg, issue):
        """"""
        if not self.tracker.check_exists(model=Issues, arg=issue):
            self.tracker.add(Issues(issue_id=issue))
            self.tracker.add(IssueStates(issue_number=issue, status_id=IssueStatus.Open.status_id, message_id=msg.id))
            self.send_message(msg.chat.id, f"Issue - {issue} added!")
        else:
            self.send_message(msg.chat.id, f"Issue - {issue} already exists!")

    def close_issue(self, msg, issue):
        """"""
        if self.tracker.check_exists(model=Issues, arg=issue):
            already_closed = self.tracker.get_one(field=(IssueStates.issue_number,),
                                                  filter=(IssueStates.issue_number == issue,
                                                          IssueStates.status_id == IssueStatus.Close.status_id))
            if not already_closed:
                self.tracker.add(IssueStates(issue_number=issue,
                                             status_id=IssueStatus.Close.status_id, message_id=msg.id))
                self.send_message(msg.chat.id, f"Issue - {issue} closed!")
            else:
                self.send_message(msg.chat.id, f"Issue - {issue} already closed!")
        else:
            self.send_message(msg.chat.id, f"Issue - {issue} not found!")

    def comment_issue(self, msg, issue):
        """"""
        self.tracker.add(IssueStates(issue_number=issue, status_id=IssueStatus.Comment.status_id, message_id=msg.id))

    def get_wordcloud(self, exclude_word: list = None):
        """"""
        if exclude_word is None:
            exclude_word = [IssueStatus.Open.command, IssueStatus.Comment.command]
        data = self.get_all(field=(Messages.message,), join=IssueStates,
                            filter=(IssueStates.status_id != IssueStatus.Close.status_id,))
        words = " ".join([x[0] for x in data])
        for ex in exclude_word:
            words = words.replace(f'/{ex}', '').strip()
        image_plot = get_wordcloud_from_issues_message(words)
        return image_plot
