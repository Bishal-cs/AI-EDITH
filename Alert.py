from os import getcwd
from winotify import Notification, audio # pip install winotify

def Alert(Text):
    toaster = Notification(
        app_id = "🌐 Edith",
        title = "Alert",
        msg = Text,
        duration ="short",
        icon = getcwd() + r"C:\Users\bisha\Desktop\AI-EDITH\Data\logo.png"
    )
    toaster.set_audio(audio.Default, loop = False)

    toaster.add_actions(label = "Click me", launch = "")
    toaster.add_actions(label = "Dismiss", launch = "")

    toaster.show()

if __name__ == "__main__":
    Alert("Hello")