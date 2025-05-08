from AppOpener import close, open as appopen
from Automation.web_open import open_website

def open_app(app):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        print(f"App not found. Opening website instead...")
        open_website(app)
        return False

def close_app(application_name):
    if "chrome" in application_name:
        pass
    else:
        try:
            close(application_name, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False
        

if __name__ == "__main__":
    open_app(input("Enter the app name: "))