from yandex_cloud_ml_sdk import YCloudML
from auth import FOLDER_ID, AUTH
import json

from entites.game_entites.prompts.prompt import Prompt


class PromptExecutor:
    def __init__(self, prompt: Prompt):
        self.prompt = prompt

    def generate(self) -> dict:
        sdk = YCloudML(folder_id=FOLDER_ID, auth=AUTH)
        print("system log: running generation...")
        result = sdk.models.completions("yandexgpt").configure(temperature=0.7).run(self.prompt.messages())
        json_result = result[0].text.strip('` \n')

        try:
            generated_data = json.loads(json_result.strip('` \n'))
        except:
            generated_data = {
                "error": "Не удалось обработать ответ модели",
                "raw_response": json_result
            }

        return generated_data
