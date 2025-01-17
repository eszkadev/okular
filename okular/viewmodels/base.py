from dataclasses import asdict, dataclass

@dataclass
class BaseViewModel:
    jenkins_api: str
    last_update_str: str
    navbar_right: str

    def as_dict(self):
        return asdict(self)