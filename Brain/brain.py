from webscout import DeepInfra

ai = DeepInfra(
    is_conversation=True,
    model= "Qwen/Qwen2-72B-Instruct",
    max_tokens=800,
    timeout=30,
    intro= "EDITH",
    filepath= r"C:\Users\bisha\Desktop\AI-EDITH\chat_history.txt",
    update_file=True,
    proxies={},
    history_offset=10250,
    act=None,
)

def Main_Brain(text):
    r = ai.chat(text)
    return r