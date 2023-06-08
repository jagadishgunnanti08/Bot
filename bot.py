# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Dict
import json
import random

# from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount, ConversationReference, Activity
from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount, CardAction, ActionTypes, SuggestedActions


class ProactiveBot(ActivityHandler):
    PRODUCTS = ["EPM", "IDENTITY", "UBA", "IT SUPPORT"]

    def __init__(self, conversation_references: Dict[str, ConversationReference]):
        self.conversation_references = conversation_references

    # Load JSON DATA
    def load_json(self, file):
        with open(file, 'r') as bot_responses:
            return json.loads(bot_responses.read())

    def get_random_responses(self):
        random_list = ["Please try writing something more descriptive",
                       "Oh! It appears something you write I don't understand yet.",
                       "Do you mind trying to rephrase that?",
                       "I'm really Sorry, I'm not able to catch that",
                       "I can't answer that, Please try asking something else"]
        list_count = len(random_list) - 1
        random_item = random.randrange(list_count)
        return random_list[random_item]

    def get_bot_response(self, user_input):
        response_data = self.load_json("bot.json")
        # return response_data
        user_response = user_input.lower()
        result = ""
        for response in response_data:
            if user_response in response["user_response"]:
                bot_response = response["bot_response"]
                result = '\n'.join(bot_response)
                break
        if result == "":
            result = self.get_random_responses()
        return result

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

    async def on_members_added_activity(
            self, members_added: ChannelAccount, turn_context: TurnContext
    ):
        """
        Send a welcome message to the user and tell them what actions they may perform to use this bot
        """

        return await self._send_welcome_message(turn_context)

    async def _send_welcome_message(self, turn_context: TurnContext):
        for member in turn_context.activity.members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.text(
                        f"Welcome to Identity Bot {member.name}."
                        f" This bot will provide you with new UPDATES."
                        f" To Know more about what I can do, Please type HELP in the chat."
                    )
                )

                # await self._send_suggested_actions(turn_context)

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Respond to the users choice and display the suggested actions again.
        """

        text = turn_context.activity.text.lower()
        if text.upper() in self.PRODUCTS:
            response_text = self._process_input(text)
            await turn_context.send_activity(MessageFactory.text(response_text))
            if text != "it support":
                return await self._send_product_suggested_actions(turn_context)
        elif text == "help":
            await self._send_suggested_actions(turn_context)
        elif "problem:" in text:
            return await self._support_response(turn_context)
        else:
            response_text = self.get_bot_response(text)
            return await turn_context.send_activity(MessageFactory.text(response_text))

    
    async def _support_response(self,turn_context: TurnContext):
        reply = "Sorry For the Inconvenience. We will get back to you."
        return await turn_context.send_activity(MessageFactory.text(reply))

    def _process_input(self, text: str):
        color_text = "Let me fetch the details of"

        if text == "identity":
            return f"{color_text} Identity"

        if text == "uba":
            return f"{color_text} UBA"

        if text == "epm":
            return f"{color_text} EPM"
        
        if text == "it support":
            return "Can you define your problem ? To test the response please start with PROBLEM: <problem>"

        return "Do you want to tell me a joke while you wait ?"

    async def _send_suggested_actions(self, turn_context: TurnContext):
        """
        Creates and sends an activity with suggested actions to the user. When the user
        clicks one of the buttons the text value from the "CardAction" will be displayed
        in the channel just as if the user entered the text. There are multiple
        "ActionTypes" that may be used for different situations.
        """

        reply = MessageFactory.text("Please select a Product")

        reply.suggested_actions = SuggestedActions(
            actions=[
                CardAction(
                    title="Identity",
                    type=ActionTypes.im_back,
                    value="Identity",
                ),
                CardAction(
                    title="UBA",
                    type=ActionTypes.im_back,
                    value="UBA",
                ),
                CardAction(
                    title="EPM",
                    type=ActionTypes.im_back,
                    value="EPM",
                ),
                CardAction(
                    title="IT Support",
                    type=ActionTypes.im_back,
                    value="IT Support",
                ),
            ]
        )

        return await turn_context.send_activity(reply)
    
    async def _send_product_suggested_actions(self, turn_context: TurnContext):
        """
        Creates and sends an activity with suggested actions to the user. When the user
        clicks one of the buttons the text value from the "CardAction" will be displayed
        in the channel just as if the user entered the text. There are multiple
        "ActionTypes" that may be used for different situations.
        """

        reply = MessageFactory.text("Please select an option")

        reply.suggested_actions = SuggestedActions(
            actions=[
                CardAction(
                    title="Releases",
                    type=ActionTypes.im_back,
                    value="Releases",
                ),
                CardAction(
                    title="Documentation",
                    type=ActionTypes.im_back,
                    value="Documentation",
                ),
                CardAction(
                    title="R&D Support",
                    type=ActionTypes.im_back,
                    value="R&D Support",
                ),
                CardAction(
                    title="Jira",
                    type=ActionTypes.im_back,
                    value="Jira",
                ),
                CardAction(
                    title="ITCC",
                    type=ActionTypes.im_back,
                    value="ITCC",
                ),
            ]
        )

        return await turn_context.send_activity(reply)