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
    PRODUCTS = ["EPM", "Identity", "UBA"]

    def __init__(self, conversation_references: Dict[str, ConversationReference]):
        self.conversation_references = conversation_references

    # Load JSON DATA
    def load_json(self, file):
        with open(file, 'r') as bot_responses:
            print(f"Load {file} Successfully!")
            return json.loads(bot_responses)

    def get_random_responses(self):
        random_list = ["Please try writing something more descriptive",
                       "Oh! It appears something you write I don't understand yet.",
                       "Do you mind trying to rephrase that?",
                       "I'm really Sorry, I'm not able to catch that",
                       "I can't answer that, Please try asking something else"]
        list_count = len(random_list) - 1
        random_item = random.randrange(list_count)
        return random_list[random_item]

    async def get_bot_response(self, user_input):
        response_data = self.load_json("bot.json")
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

    # async def on_members_added_activity(
    #     self, members_added: ChannelAccount, turn_context: TurnContext
    # ):
    #     for member in members_added:
    #         if member.id != turn_context.activity.recipient.id:
    #             await turn_context.send_activity(
    #                 "Welcome to the Proactive Bot sample.  Navigate to "
    #                 "http://localhost:3978/api/notify to proactively message everyone "
    #                 "who has previously messaged this bot."
    #             )

    # async def on_message_activity(self, turn_context: TurnContext):
    #     self._add_conversation_reference(turn_context.activity)
    #     return await turn_context.send_activity(
    #         f"You sent: {turn_context.activity.text}"
    #     )

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

    async def on_message_activity(self, turn_context: TurnContext):
        """
        Respond to the users choice and display the suggested actions again.
        """

        text = turn_context.activity.text.lower()
        response_text = self._process_input(text)

        await turn_context.send_activity(MessageFactory.text(response_text))

        return await self._details(text, turn_context)

    async def _details(self, text: str, turn_context: TurnContext):
        product = text.upper()
        if product in self.PRODUCTS:
            product_text = f"There is a !!! BIG UPDATE !!! coming in TWO weeks for {product}"
        else:
            product_text = self.get_bot_response(user_input=product.lower())

        reply = MessageFactory.text(product_text)
        # await turn_context.send_activity(
        #             MessageFactory.text(product_text)
        #             )
        return await turn_context.send_activity(reply)

    async def _send_welcome_message(self, turn_context: TurnContext):
        for member in turn_context.activity.members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.text(
                        f"Welcome to Identity Bot {member.name}."
                        f" This bot will introduce you to suggestedActions and Updates."
                    )
                )

                await self._send_suggested_actions(turn_context)

    def _process_input(self, text: str):
        color_text = "Let me fetch the details of"

        if text == "identity":
            return f"{color_text} Identity"

        if text == "uba":
            return f"{color_text} UBA"

        if text == "epm":
            return f"{color_text} EPM"

        if text != "" and text.upper() not in self.PRODUCTS:
            return text

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
                    # image="https://via.placeholder.com/20/FF0000?text=R",
                    # image_alt_text="R",
                ),
                CardAction(
                    title="UBA",
                    type=ActionTypes.im_back,
                    value="UBA",
                    # image="https://via.placeholder.com/20/FFFF00?text=Y",
                    # image_alt_text="Y",
                ),
                CardAction(
                    title="EPM",
                    type=ActionTypes.im_back,
                    value="EPM",
                    # image="https://via.placeholder.com/20/0000FF?text=B",
                    # image_alt_text="B",
                ),
            ]
        )

        return await turn_context.send_activity(reply)