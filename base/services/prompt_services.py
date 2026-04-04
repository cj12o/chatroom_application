from django.conf import settings
import os
from base.logger import logger

def get_prompt(prompt_file:str):
    base_dir=settings.BASE_DIR
    path=os.path.join(base_dir,"base","prompts",prompt_file)
    if not os.path.exists(path):
        logger.error(f"Prompt file {prompt_file} not found")
        return ""
    with open(path) as f:
        prompt = f.read()
    return prompt

