import dataiku
import meaningcloud
import pandas as pd
from dataiku.customrecipe import (
    get_input_names_for_role,
    get_output_names_for_role,
    get_recipe_config,
    get_plugin_config,
)
from meaningcloud_common import setRequestSource, isBlockingErrorType


# ==============================================================================
# PLUGIN + RECIPE SETTINGS
# ==============================================================================

input_name = get_input_names_for_role("input_dataset")[0]
output_name = get_output_names_for_role("output_dataset")[0]

input_dataset = dataiku.Dataset(input_name)
output_dataset = dataiku.Dataset(output_name)


meaningcloud_connection = get_plugin_config().get("meaningcloud_connection")

license_key = meaningcloud_connection.get("license_key", None)
server = meaningcloud_connection.get(
    "meaningcloud_server", "https://api.meaningcloud.com"
)
text_column = get_recipe_config().get("column_name", None)


# ==============================================================================
# AUXILIARY FUNCTIONS
# ==============================================================================

# Analyzes the text passed as a parameter
def analyzeText(text):
    global index_count
    print("Identifying language for text #%s" % str(index_count))

    # this is where we are going to store our results
    language_code = ""
    language_name = ""

    try:
        # We are going to make a request to the Language Identification API
        request = meaningcloud.LanguageRequest(license_key, txt=text, server=server)
        setRequestSource(request)
        response = meaningcloud.LanguageResponse(request.sendReq())
        if response.isSuccessful():
            lang = response.getFirstLanguage()
            if lang:
                language_code = response.getLanguageCode(lang)
                language_name = response.getLanguageName(lang)
        else:
            if isBlockingErrorType(response.getStatusCode()):
                raise ValueError(
                    "Something went wrong in the MeaningCloud request!: ("
                    + response.getStatusCode()
                    + ") "
                    + response.getStatusMsg()
                )
            else:
                print(
                    "Oops! The request to Language Identification for text #"
                    + str(index_count)
                    + " was not succesful: ("
                    + response.getStatusCode()
                    + ") "
                    + response.getStatusMsg()
                )
                language_code = (
                    "ERROR ("
                    + response.getStatusCode()
                    + "): "
                    + response.getStatusMsg()
                )

    except ValueError as e:
        raise ValueError(str(e))

    index_count += 1

    return pd.Series([language_code, language_name])


# ==============================================================================
# MAIN FLOW
# ==============================================================================

if text_column is None or len(text_column) == 0:
    raise ValueError("You must specify the input text column.")

if not input_dataset:
    raise ValueError("No input dataset specified!")

input_df = input_dataset.get_dataframe()

if text_column not in input_df:
    raise ValueError("The column configured does not exist in the data input!")


print("Starting analysis for %d texts... " % (len(input_df)))

output_df = input_df

# main analysis
index_count = 1
label_list = ["language_code", "language_name"]
output_df[label_list] = input_df[text_column].apply(analyzeText)

# write results
output_dataset.write_with_schema(output_df)
