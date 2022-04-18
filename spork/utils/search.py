# Regisiter devices into search system

from ..logger import logger

log = logger(__name__)

drivers = {}

__all__ = ["catalog"]


class Catalog:
    "A catalogue of registered things"

    def __init__(self):
        self.sections = {}

    def insert(self, section, name, cls):
        if section not in self.sections:
            self.sections[section] = {name: [cls]}
        else:
            current_section = self.sections[section]
            if name in current_section:
                current_section[name].append(cls)
            else:
                current_section[name] = [cls]


catalog = Catalog()


def Enroll(**info):
    "Wrapper for registering meta data of constructs"

    def inner(cls):
        for section, name in info.items():
            log.debug("Peripheral : %s - %s - %s", section, name, cls.__name__)
            if isinstance(name, str):
                catalog.insert(section, name, cls)
            elif isinstance(name, list):
                for item in name:
                    catalog.insert(section, item, cls)
        return cls

    return inner
