from dataclasses import astuple, dataclass

@dataclass
class BaseViewModel:
    jenkins_api: str
    last_update_str: str
    navbar_right: str = ''