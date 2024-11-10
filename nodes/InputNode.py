from nodes.BaseGraphNode import BaseGraphNode
import os
from openai import OpenAI

class InputNode(BaseGraphNode):
    def __init__(self, name : str = '', **kwargs):
        super().__init__(name, **kwargs)