# nmigen fetcher
import os, importlib

from ..logger import logger

log = logger(__name__)

repos = {
    "nmigen": "https://github.com/nmigen/nmigen",
    "nmigen-soc": "https://github.com/nmigen/nmigen-soc",
    "nmigen-boards": "https://github.com/nmigen/nmigen-boards",
    "nmigen-stdio": "https://github.com/nmigen/nmigen-stdio",
    "minerva": "https://github.com/lambdaconcept/minerva.git",
    "Boneless-CPU": "https://github.com/whitequark/Boneless-CPU",
}


def check_install(directory):
    log.critical("Check directory Unfinished")
    pass


def update_install(directory):
    log.critical("Update directory Unfinished")
    pass


# Transplant for elsewhere pls ignore
def Fetch(item):
    name = item[0]
    url = item[1]
    path = "lib" + os.sep + name
    print(name, url, path)
    try:
        r = Repo(path)
    except:
        print(name + " does not exist , creating")
        r = Repo.init(path)
        r.create_remote("origin", url)
        r.remotes.origin.pull("master")
    return r


def FetchAll():
    local_repos = []
    for i in repos.items():
        local_repos.append(Fetch(i))
    return local_repos


r = FetchAll()
print(r)
