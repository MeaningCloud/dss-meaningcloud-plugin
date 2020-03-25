# When creating plugins, it is a good practice to put the specific logic in libraries and keep plugin components (recipes, etc) short. 
# You can add functionalities to this package and/or create new packages under "python-lib"
import re

def isBlockingErrorType(code):
    if re.match(r'(10[015]|20[1567])', code):
        return True

def insertInList(list_to_use, value):
    if value not in list_to_use:
        list_to_use.append(value)

def setRequestSource(request):
    version = '1.0.0'
    request.addParam('src', 'dataiku-' + version)
