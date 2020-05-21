import os
import requests


class ShadertoyApiError(Exception):
    pass


class ShadertoyAPI:
    def __init__(self):
        self.api_key = os.environ['API_KEY']

    def _request_shader(self, shader_id):
        response = requests.get(f"https://www.shadertoy.com/api/v1/shaders/{shader_id}?key={self.api_key}")
        return response

    def get_shader_passes(self, shader_id):
        response = self._request_shader(shader_id)
        if response.status_code != 200:
            raise response.reason
        response_json = response.json()
        if 'Error' in response_json:
            raise ShadertoyApiError(response_json['Error'])
        renderpasses = response_json['Shader']['renderpass']
        code = []
        for renderpass in renderpasses:
            code.append(renderpass['code'])
        return code
