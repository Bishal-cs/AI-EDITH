import random
online_dlg = [
    "sir i am online and ready to help you",
    "sir i am online and ready",
    "sir i am online",
    "sir i am ready",
    "sir i am ready to help you",
    "sir i am online to assist you",
    "sir i am online and prepared",
    "sir i am online and available",
    "sir i am here online to help",
    "sir i am online and at your service",
    "sir i am available online",
    "sir i am online and eager to help",
    "sir i am online and waiting to assist",
    "sir i am online and here to help",
    "sir i am online and ready to serve",
    "sir i am online and here for you",
    "sir i am ready online",
    "sir i am ready to assist you online",
    "sir i am online and standing by",
    "sir i am online and good to go",
    "I'm here and fully operational.",
    "Online and ready to assist you.",
    "Standing by, ready to help.",
    "I'm online and at your service.",
    "Ready to go whenever you are.",
    "I'm here, ready to assist.",
    "Activated and prepared to help.",
    "Online, let's get started.",
    "Ready and waiting for your command.",
    "I'm live and ready to assist.",
    "System's up, how can I help?",
    "I'm here, fully online.",
    "Online, awaiting your instructions.",
    "Good to go, what's next?",
    "Connected and ready to assist.",
    "I'm online, what can I do for you?",
    "Ready for action, just say the word.",
    "I'm online and standing by.",
    "Fully connected, ready to assist.",
    "Here to help, fully operational.",
    "I'm active and ready for your orders.",
    "Online and prepared to assist.",
    "System's ready, how can I assist?",
    "I'm ready and waiting for your lead.",
    "I'm here, fully powered up and ready."
    "sir i am online and ready to provide assistance",
    "sir i am here online and ready",
    "sir i am online and on standby",
    "sir i am online and set to help",
    "sir i am online and at your disposal",
    "sir i am online and ready to offer help",
    "sir i am online and ready to give assistance",
    "sir i am online and ready to aid you",
    "sir i am online and prepared to help",
    "sir i am online and waiting to help",
    "sir i am online and at the ready",
    "sir i am online and on hand to help",
    "sir i am online and ready to respond",
    "sir i am online and ready to assist you now",
    "sir i am online and available to help",
    "sir i am online and here to assist you",
    "sir i am online and ready to support you",
    "sir i am online and ready for assistance",
    "sir i am online and ready for your instructions",
    "sir i am online and here to serve",
    "sir i am online and prepared to assist",
    "sir i am online and prepared to serve",
    "sir i am online and prepared to aid you",
    "sir i am online and here to give assistance",
    "sir i am online and standing by to help",
    "sir i am online and set to assist you",
    "sir i am online and available to assist",
    "sir i am online and here to help you",
    "sir i am online and ready to work",
    "sir i am online and prepared to support",
    "sir i am online and ready to engage",
    "sir i am online and available for help",
    "sir i am online and here to support you",
    "sir i am online and ready to collaborate",
    "sir i am online and ready to contribute",
    "sir i am online and ready to engage",
    "sir i am online and here to collaborate",
    "sir i am online and available to serve",
    "sir i am online and prepared for your instructions",
    "sir i am online and set to provide assistance",
    "sir i am online and eager to assist",
    "sir i am online and ready to assist you immediately",
    "sir i am online and waiting for your instructions",
    "sir i am online and ready to support your needs",
    "sir i am online and here to assist you promptly",
    "sir i am online and ready to aid",
    "sir i am online and here to give support",
    "sir i am online and ready to cooperate",
    "sir i am online and ready to assist you today",
    "sir i am online and waiting to help you",
    "sir i am online and here to assist you now",
    "sir i am online and available for assistance",
    "sir i am online and prepared to give assistance",
    "sir i am online and ready to support you now",
    "sir i am online and here to help right away",
    "sir i am online and ready to serve you",
    "sir i am online and prepared to cooperate",
    "sir i am online and here to help immediately",
    "sir i am online and ready to support your efforts",
    "sir i am online and eager to assist you",
    "sir i am online and available to help right now",
    "sir i am online and ready to help you immediately",
    "sir i am online and here to provide support",
    "sir i am online and ready to assist right away",
    "sir i am online and standing by to support",
    "sir i am online and prepared to support you",
    "sir i am online and available to assist you now",
    "sir i am online and ready to help you today",
    "sir i am online and eager to provide help",
    "sir i am online and prepared to give support",
    "sir i am online and here to assist you promptly",
    "sir i am online and ready to help you promptly",
    "sir i am online and waiting to provide help",
    "sir i am online and prepared to offer support",
    "sir i am online and ready to serve you now",
    "sir i am online and waiting to serve",
    "sir i am online and ready to help you now",
    "sir i am online and standing by to assist you",
    "sir i am online and ready to support you immediately",
    "sir i am online and available to help you now",
]
offline_dlg = [
    "sir i am offline please connect me to internet",
    "sir i am offline please connect me to the internet",
    "sir i am offline",
    "sir i am not connected to the internet",
    "sir i am not online please connect me to internet",
    "sir i am offline can you connect me to internet",
    "sir i am offline please connect me",
    "sir i am offline please check the internet connection",
    "sir i am offline i need an internet connection",
    "sir i am offline please provide internet access",
    "sir i am offline i need to be connected to internet",
    "sir i am offline can you provide internet",
    "sir i am offline please enable internet",
    "sir i am offline please reconnect me to internet",
    "sir i am offline reconnect me to internet please",
    "sir i am offline please fix the internet connection",
    "sir i am offline internet connection needed",
    "sir i am offline please connect to the internet",
    "sir i am offline please get me online",
    "sir i am offline internet access required",
    "sir i am offline please establish internet connection",
    "sir i am offline internet connection required",
    "sir i am offline please connect me",
    "sir i am offline reconnect internet please",
    "sir i am offline internet needed",
    "sir i am offline please connect",
    "sir i am offline check internet connection",
    "sir i am offline connect me to internet",
    "sir i am offline connect to internet please",
    "sir i am offline please enable the internet",
    "sir i am offline reconnect me to the internet",
    "sir i am offline need internet access",
    "sir i am offline internet connection needed",
    "sir i am offline please provide internet",
    "sir i am offline please get internet",
    "sir i am offline please fix internet",
    "sir i am offline connect internet",
    "sir i am offline check the internet",
    "sir i am offline need connection",
    "sir i am offline connect me",
    "sir i am offline enable internet",
    "sir i am offline reconnect internet",
    "sir i am offline please enable connection",
    "sir i am offline need internet",
    "sir i am offline get me online",
    "sir i am offline connect internet please",
    "sir i am offline please check connection",
    "sir i am offline fix internet",
    "sir i am offline please connect internet",
    "sir i am offline provide internet",
    "sir i am offline please reconnect",
    "sir i am offline need access",
    "sir i am offline enable connection",
    "sir i am offline establish connection",
    "sir i am offline fix connection",
    "sir i am offline reconnect please",
    "sir i am offline internet access needed",
    "sir i am offline reconnect to internet",
    "sir i am offline internet connection required",
    "sir i am offline please establish connection",
    "sir i am offline please get internet",
    "sir i am offline please fix the connection",
    "sir i am offline please connect internet",
    "sir i am offline connect me to the internet",
    "sir i am offline i need internet access",
    "sir i am offline please get online",
    "sir i am offline please reconnect me",
    "sir i am offline connect me please",
    "sir i am offline need connection please",
    "sir i am offline enable the internet",
    "sir i am offline provide connection",
    "sir i am offline connect to the internet",
    "sir i am offline internet access required",
    "sir i am offline establish internet connection",
    "sir i am offline reconnect me",
    "sir i am offline check the connection",
    "sir i am offline need internet connection",
    "sir i am offline reconnect to the internet",
    "sir i am offline please fix connection",
    "sir i am offline need internet",
    "sir i am offline connect to internet",
    "sir i am offline reconnect connection",
    "sir i am offline provide access",
    "sir i am offline enable internet please",
    "sir i am offline fix the connection",
    "sir i am offline please connect",
    "sir i am offline enable the connection",
    "sir i am offline connect to internet please",
    "sir i am offline get me internet",
    "sir i am offline fix internet connection",
    "sir i am offline reconnect to internet please",
    "sir i am offline need internet access",
    "sir i am offline internet connection needed",
    "sir i am offline connect me online",
    "sir i am offline internet access needed",
    "sir i am offline reconnect me to internet",
    "sir i am offline get online please",
    "sir i am offline fix the internet",
    "sir i am offline provide internet access",
]