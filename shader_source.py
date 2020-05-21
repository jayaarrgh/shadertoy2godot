import os
import requests


class GetShaderCode:
    def __init__(self):
        self.api_key = os.environ['API_KEY']

    def _request_shader(self, shader_id):
        response = requests.get(f"https://www.shadertoy.com/api/v1/shaders/{shader_id}?key={self.api_key}")
        return response

    def get_shades(self, shader_id):
        response = self._request_shader(shader_id)
        if response.status_code != 200:
            return None
        renderpasses = response.json()['Shader']['renderpass']
        code = []
        for renderpass in renderpasses:
            code.append(renderpass['code'])
        return code
