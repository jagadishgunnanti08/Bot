from typing import Dict
from jira import JIRA
from botbuilder.schema import ConversationReference, Activity
from botbuilder.core import ActivityHandler, TurnContext

class ProactiveBot(ActivityHandler):
    def __init__(self, conversation_references: Dict[str, ConversationReference]):
        self.conversation_references = conversation_references
    
    async def on_conversation_update_activity(self, turn_context: TurnContext):
        self._add_conversation_reference(turn_context.activity)
        return await super().on_conversation_update_activity(turn_context)

    def _add_conversation_reference(self, activity: Activity):
        """
        This populates the shared Dictionary that holds conversation references. In this sample,
        this dictionary is used to send a message to members when /api/notify is hit.
        :param activity:
        :return:
        """
        conversation_reference = TurnContext.get_conversation_reference(activity)
        self.conversation_references[
            conversation_reference.user.id
        ] = conversation_reference

    async def on_message_activity(self, turn_context):

        user_input = turn_context.activity.text
        user_input = user_input.lower()
    
        if user_input == "jira":

            jira_api_url = 'https://identity-bot.atlassian.net/'
            jira_username = 'jagadish.gunnanti@cyberark.com'
            jira_api_token = 'ATATT3xFfGF0OI8RBTwoiXqj8wSpCVAzl9z90PR9fxBzXEabuvReWpOENQgfb7uuI24TQIoHg5JdNYCAte5JJ_AOq4npiRci0eD1cIrIzMjlNStIZVAOzwgAGxSDEcOQ4wGmzx87VIhjNRgXa4MVNSzkeTYuTIudY064nURKvpb1L_T2fBqljE8=7130DB82'

            jira = JIRA(server=jira_api_url, basic_auth=(jira_username, jira_api_token))

            issue = {
                'project': {'key': "BP"},
                'summary': 'Test Summary from Bot',
                'description': 'Test Description from Bot',
                'issuetype': {'name': 'Task'},
            }
            new_issue = jira.create_issue(fields=issue)

            await turn_context.send_activity(f"Jira ticket {new_issue.key} has been created, our support team will get back to you!")