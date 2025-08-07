from yandex_cloud_ml_sdk import YCloudML
from auth import FOLDER_ID, AUTH
import json

from entites.game_entites.prompts.prompt import Prompt


class PromptExecutor:
    def __init__(self, prompt: Prompt):
        self.prompt = prompt

    def generate(self) -> dict:
        text = self.generate_text()
        try:
            generated_data = json.loads(text.strip('` \n'))
        except:
            generated_data = {
                "error": "Не удалось обработать ответ модели",
                "raw_response": text
            }

        return generated_data

    def generate_text(self):
        sdk = YCloudML(folder_id=FOLDER_ID, auth=AUTH)
        print("system log: running generation...")
        result = sdk.models.completions("yandexgpt").configure(temperature=0.7).run(self.prompt.messages())
        text_result = result[0].text.strip('` \n')
        return text_result
