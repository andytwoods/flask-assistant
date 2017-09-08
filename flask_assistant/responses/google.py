# TODO texttospeech mutually exclusive with ssml


class _GoogleData():
    """Represents the data.google object of the _ApiAiResponse.

    The _GoogleData object is not to be rendered as a response but rather
    to extend an existing response to be returned to Api.AI. It contains all the
    data required for communicating with Actions on Google via Api.AI.

    The data is sent to the client in the original form and is not processed by API.AI.

    Note that the contents of this class mirror the Actions API.AI webhook format,
    which closely resembles but is not identical to the Conversation webhook API.ai

    
    Migration guide - https://developers.google.com/actions/reference/v1/migration#apiai_webhook_protocol_changes
    Webhook Response format - https://developers.google.com/actions/apiai/webhook

    #InputPrompt.FIELDS.rich_initial_prompt
    Relavent Field for RIch Response - https://developers.google.com/actions/reference/rest/Shared.Types/AppResponse
    #ExpectedInput.FIELDS.possible_intents
    Relavent field for SystemIntent - https://developers.google.com/actions/reference/rest/Shared.Types/AppResponse

    V1 info - https://developers.google.com/actions/reference/v1/apiai-webhook

    Sample Responses - https://developers.google.com/actions/assistant/responses

    Example Google Data Object:

    """

    def __init__(self):
        super(_GoogleData, self).__init__()

        self.speech = ''
        self.display_text = ''
        self.expect_response = True

        self.rich_response = _RichResponse()
        self.system_intent = {}

        self.intent = ''
        self.input_data = {}
        self._data = {}

    def simple_response(self, speech, display_text, expect_response):
        self.speech = speech
        self.display_text = display_text
        self.expect_response = expect_response

        self.rich_response.add_simple_response_item(speech, display_text)

        expected_intent = _SystemIntent('TEXT')._load_data()
        self.system_intent = expected_intent

        return self._load_data()

    def suggestion(self, title):
        self.rich_response.add_suggestion(title)
        # expected_intent = _SystemIntent('TEXT')._load_data()
        # self.system_intent = expected_intent
        return self._load_data()

    def link_out(self, dest, url):
        self.rich_response.add_link_out(dest, url)
        return self._load_data()

    def _load_data(self):
        self._data['speech'] = self.speech
        self._data['expectUserResponse'] = self.expect_response
        # The ssml field in a SimpleResponse. IGNORED IN V2
        self._data['isSsml'] = True
        self._data['finalResponse'] = {}

        # optional?
        self._data['noInputPrompts'] = []

        # A RichResponse in an expectedInputs.inputPrompt.richInitialPrompt
        self._data['richResponse'] = self.rich_response._load_data()

        # replaces expectedInputs.possibleIntents
        self._data['systemIntent'] = self.system_intent
        return self._data


class _RichResponse():
    """docstring for _RichResponse"""

    def __init__(self):
        self.items = []
        self.suggestions = []
        self.link_out = {}

        self._data = {}

    def _load_data(self):
        self._data['items'] = self.items
        if self.suggestions:
            self._data['suggestions'] = self.suggestions
        if self.link_out:
            self._data['linkOutSuggestion'] = self.link_out
        return self._data

    def add_simple_response_item(self, speech, display_text):
        """Builds a simple response containing speech or text to show the user

        Every _RichResponse requires this type of response as the first item

        This object does not include the ssml field found in the Actions API
        because API.ai formats the ssml based off the value of data.google.isSsml
        """

        simple = {'textToSpeech': speech, 'displayText': display_text}
        payload = {'simpleResponse': simple}
        self.items.append(payload)


    def add_suggestion(self, title):
        """Provides a suggestion chip that the user can tap to quickly post a reply to the conversation

            If used in a FinalResponse, they will be ignored.
        """
        suggestion = {'title': title}
        self.suggestions.append(suggestion)

    def add_link_out(self, dest, url):
        """An additional suggestion chip that can link out to the associated app or site."""
        if len(self.link_out) > 0:
            raise ValueError('Only one linkOutSuggestion may be given')

        payload = {
            'destinationName': dest,
            'url': url
        }
        self.link_out = payload


class _SystemIntent(object):
    """Defines expected (Actions) intent along with extra config data

        This represents the type of data to be received from the user.

        To have the Google Assistant just return the raw user input,
        the app should ask for the actions.intent.TEXT intent.

        Possible intents:
            TEXT
            OPTION
            CONFIRMATION
            TRANSACTION_REQUIREMENTS_CHECK
            DELIVERY_ADDRESS
            TRANSACTION_DECISION

        https://developers.google.com/actions/components/intents
        https://developers.google.com/actions/reference/rest/Shared.Types/AppResponse#ExpectedIntent
    """

    def __init__(self, intent='text'):

        self.intent = 'actions.intent.{}'.format(intent.upper())
        self.input_value_data = {}

        if 'OPTION' in self.intent:
            self.input_value_data = OptionValueSpec()

    def _load_data(self):
        if self.input_value_data is None:
            return {'intent': self.intent}
        return {'intent': self.intent, 'inputValueData': self.input_value_data}


class OptionValueSpec():
    """Presents a selector and Asks the user to select one of the options.

    The type of selector presented can be only one of the following:

        simpleSelect, listSelect, carouselSelect"""

    def __init__(self):
        super(OptionValueSpec, self).__init__()

    @staticmethod
    def build_option_item(key, synonyms=None, title=None):
        """Builds an option item to be presented in a selector

        Follows a slightly different format than List or Carousel Items

        Arguments:
            key {str} -- A unique key that will be sent back
                        to the agent if this response is given. (default: {None})

        Keyword Arguments:
            synonyms {list} -- synonyms that can also be used to trigger this item in dialog.
            title {str} -- Title of the item. It will act as synonym if it's provided (default: {None})

        Returns:
            dict -- item object to be included in a simpleSelect selector
        """

        if synonyms is None:
            synonyms = []

        item = {}
        item['optionInfo'] = {'key': key, 'synonyms': synonyms}

        if title is not None:
            item['title'] = title

        return item

    @staticmethod
    def build_list_item(key, title, synonyms, description=None, image=None):
        """Builds an item that may be added to List or Carousel"""
        item = OptionValueSpec.build_option_item(key, synonyms, title)
        item['description'] = description
        item['image'] = image  # TODO: implement Image object
        return item

    def add_simple_select(self, items):  # TODO: HEREE
        """A simple select with no associated GUI"""

    def add_list_select(self):
        """A select with a list card GUI"""
        pass

    def add_carouselSelect(self):
        """A select with a card carousel GUI"""
        pass
