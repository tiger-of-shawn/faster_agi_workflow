from BaseGraphNode import BaseGraphNode
import os
from openai import OpenAI

class LlmNode(BaseGraphNode):
    def __init__(self, name : str = '', **kwargs):
        super().__init__(name, **kwargs)
        self.input_keys = ['user_prompt']
        self.output_keys = ['llm_response']
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.model = 'qwen-max'

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
                    print(f"Processing: {data}")
                    if 'user_prompt' not in data:
                        continue
                    completion = self.client.chat.completions.create(
                        model=self.model, # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                        messages=[{"role": "user", "content": data['user_prompt']}]
                    )
                    llm_response = completion.choices[0].message.content
                    for callback in self.output_callbacks:
                        callback(key = 'llm_response', value = llm_response)
                else:
                    # This should not happen because we only acquire when there's data
                    print("Unexpected state: semaphore acquired but no data")


def llm_response(key: str, value: any) -> None:
    print(f'key = {key}, value = {value}')

if __name__ == '__main__':
    llmNode = LlmNode(name = 'llm_node')

    print(f'input keys: {llmNode.get_input_keys()}')
    print(f'output keys: {llmNode.get_output_keys()}')

    llmNode.register_output_callback(llm_response)
    llmNode.run()
    data_to_infer = {'user_prompt': 'What is the capital of China?'}

    llmNode.set_input(**data_to_infer)
    

