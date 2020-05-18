import dataiku
import meaningcloud
import pandas as pd
from dataiku.customrecipe import (
    get_input_names_for_role,
    get_output_names_for_role,
    get_recipe_config,
    get_plugin_config,
)
from meaningcloud_common import isBlockingErrorType, setRequestSource

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
    "meaningcloud_server", "https://api.meaningcloud.com/"
)
text_column = get_recipe_config().get("column_name", None)
model = get_recipe_config().get("model", None)
user_model = get_recipe_config().get("user_model", None)
if user_model is not None and user_model != "":
    model = user_model
else:
    model = model + "_" + get_recipe_config().get("language")
categories = int(get_recipe_config().get("categories", 1))


# ==============================================================================
# AUXILIARY FUNCTIONS
# ==============================================================================


# Analyzes the text passed as a parameter
def analyzeText(text, model, num_cats):
    global index_count
    print("Classifying text #%s" % str(index_count))

    # this is where we are going to store our results
    formatted_categories = ""

    try:
        # We are going to make a request to the Deep Categorization API
        request = meaningcloud.DeepCategorizationRequest(
            license_key, model=model, txt=text, server=server
        )
        setRequestSource(request)
        response = meaningcloud.DeepCategorizationResponse(request.sendReq())

        if response.isSuccessful():
            categories = response.getCategories()
            formatted_categories = [
                response.getCategoryLabel(cat) for cat in categories[:num_cats]
            ]
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
                    "Oops! The request to Deep Categorization for text #"
                    + str(index_count)
                    + " was not succesful: ("
                    + response.getStatusCode()
                    + ") "
                    + response.getStatusMsg()
                )
                formatted_categories = [
                    "ERROR ("
                    + response.getStatusCode()
                    + "): "
                    + response.getStatusMsg()
                ]

    except ValueError as e:
        raise ValueError(str(e))

    index_count += 1

    formatted_categories = formatted_categories + [""] * (
        num_cats - len(formatted_categories)
    )
    return pd.Series(formatted_categories)


# ==============================================================================
# MAIN FLOW
# ==============================================================================

if text_column is None or len(text_column) == 0:
    raise ValueError("You must specify the input text column.")

if model is None:
    raise ValueError(
        "You must specify the model you want to use in the classification."
    )

if not input_dataset:
    raise ValueError("No input dataset specified!")

input_df = input_dataset.get_dataframe()

if text_column not in input_df:
    raise ValueError("The column configured does not exist in the data input!")


print("Starting analysis for %d texts using '%s'... " % (len(input_df), model))

output_df = input_df

# main analysis
index_count = 1
label_list = ["category_" + str(n + 1) for n in range(categories)]
output_df[label_list] = input_df[text_column].apply(
    analyzeText, model=model, num_cats=categories
)

# write results
output_dataset.write_with_schema(output_df)
