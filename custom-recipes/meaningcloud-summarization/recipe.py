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
sentences = int(get_recipe_config().get("sentences", 5))
text_column = get_recipe_config().get("column_name", None)


# ==============================================================================
# AUXILIARY FUNCTIONS
# ==============================================================================

# Analyzes the text passed as a parameter


def analyzeText(text):
    global index_count
    print("Extracting summary for text #%s" % str(index_count))

    # this is where we are going to store our results
    summary = ""

    try:
        # We are going to make a request to the Summarization API
        request = meaningcloud.SummarizationRequest(
            license_key, sentences=sentences, txt=text, server=server
        )
        setRequestSource(request)
        response = meaningcloud.SummarizationResponse(request.sendReq())
        if response.isSuccessful():
            summary = response.getSummary()
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
                    "Oops! The request to Summarization for text #"
                    + str(index_count)
                    + " was not succesful: ("
                    + response.getStatusCode()
                    + ") "
                    + response.getStatusMsg()
                )
                summary = (
                    "ERROR ("
                    + response.getStatusCode()
                    + "): "
                    + response.getStatusMsg()
                )

    except ValueError as e:
        raise ValueError(str(e))

    index_count += 1

    return pd.Series([summary])


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
label_list = ["summary"]
output_df[label_list] = input_df[text_column].apply(analyzeText)

# write results
output_dataset.write_with_schema(output_df)
