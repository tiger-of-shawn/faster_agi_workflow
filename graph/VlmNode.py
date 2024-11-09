from BaseGraphNode import BaseGraphNode
import os
from openai import OpenAI

class VlmNode(BaseGraphNode):
    def __init__(self, name : str = '', **kwargs):
        super().__init__(name, **kwargs)
        self.input_keys = ['user_prompt', 'base64_image']
        self.output_keys = ['llm_response']
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.model = 'qwen-vl-max-latest'

        for key, value in kwargs.items():
            if 'base_url' == key:
                self.base_url = value
            if 'api_key' == key:
                self.api_key = value
            if 'model' == key:
                self.model = value
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def process_data(self):
        while self.running:
            self.data_semaphore.acquire()  # Decrement the semaphore, wait for new data
            with self.data_lock:
                if self.input_data:
                    data = self.input_data.pop(0)
                    if 'user_prompt' not in data or 'base64_image' not in data:
                        continue
                    print(f"Processing: {data['user_prompt']}")
                    completion = self.client.chat.completions.create(
                        model = self.model, # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                        messages = [
                                    {
                                        "role": "user",
                                        "content": [
                                            {
                                                "type": "image_url",
                                                "image_url": {"url": f"data:image/jpeg;base64,{data['base64_image']}"},
                                            },
                                            {"type": "text", "text": data['user_prompt']},
                                        ],
                                    }
                                ]
                    )
                    llm_response = completion.choices[0].message.content
                    for callback in self.output_callbacks:
                        callback(key = 'llm_response', value = llm_response)
                else:
                    # This should not happen because we only acquire when there's data
                    print("Unexpected state: semaphore acquired but no data")


def llm_response(key: str, value: any) -> None:
    print(f'key = {key}, value = {value}')

import base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        print(f'calc base64')
        return base64.b64encode(image_file.read()).decode("utf-8")

if __name__ == '__main__':
    vlmNode = VlmNode(name = 'llm_node')

    print(f'input keys: {vlmNode.get_input_keys()}')
    print(f'output keys: {vlmNode.get_output_keys()}')

    vlmNode.register_output_callback(llm_response)
    vlmNode.run()
    data_to_infer = {'user_prompt': 'What can you see in the image?', 'base64_image': encode_image('assets/tp.jpg')}

    vlmNode.set_input(**data_to_infer)
    

