from dataclasses import dataclass

import os
import requests


@dataclass
class GetShaderCode:
    shade_id: str
    api_key: str = os.environ['API_KEY']

    def _request_shade(self):
        response = requests.get(f"https://www.shadertoy.com/api/v1/shaders/{self.shade_id}?key={self.api_key}")
        return response

    def get_shades(self):
        response = self._request_shade()
        if response.status_code != 200:
            return None
        shader_info = response.json()['Shader']['renderpass']
        code = []
        for shade in shader_info:
            code.append(shade['code'])
        return code
