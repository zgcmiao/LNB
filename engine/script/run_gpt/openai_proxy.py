import os

import requests

proxy_server_url = os.environ['PROXY_SERVER_URL']


class APIProxy:
    def __init__(self, entry, parent):
        self.entry = entry
        self.parent = parent

    def create(self, **kwargs):
        headers = {}
        if self.parent.api_key:
            headers['Authorization'] = f'Bearer {self.parent.api_key}'
        assert proxy_server_url, 'No proxy server.'
        resp = requests.post(
            f'{proxy_server_url}/{self.entry}',
            json=kwargs,
            headers=headers
        )
        resp.raise_for_status()
        return resp.json()


class OpenAIProxy:
    def __init__(self):
        self.Completion = APIProxy(entry='Completion', parent=self)
        self.ChatCompletion = APIProxy(entry='ChatCompletion', parent=self)
        self.api_key = ''


class Session:
    def __init__(self, model_name='gpt-4', chat_mode=True):
        self.model_name = model_name
        self.chat_mode = chat_mode
        self.history = []

    def input(self, msg: str):
        if self.chat_mode:
            self.history.append({
                'role': 'user',
                'content': msg
            })
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=self.history,
            )
            reply = response['choices'][0]['message']
            self.history.append(reply)
            return reply['content']
        else:
            self.history.append(msg)
            response = openai.Completion.create(
                model=self.model_name,
                prompt=''.join(self.history),
            )
            reply = response['choices'][0]['text']
            self.history.append(reply)
            return reply


openai = OpenAIProxy()
