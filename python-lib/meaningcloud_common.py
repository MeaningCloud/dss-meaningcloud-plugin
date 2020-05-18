import re


def isBlockingErrorType(code):
    if re.match(r"(10[015]|20[1567])", code):
        return True


def insertInList(list_to_use, value):
    if value not in list_to_use:
        list_to_use.append(value)


def setRequestSource(request):
    version = "1.0.1"
    request.addParam("src", "dataiku-" + version)
