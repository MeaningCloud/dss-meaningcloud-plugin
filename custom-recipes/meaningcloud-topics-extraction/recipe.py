# coding=utf-8
import dataiku
import meaningcloud
import pandas as pd
from dataiku.customrecipe import (
    get_input_names_for_role,
    get_output_names_for_role,
    get_recipe_config,
    get_plugin_config,
)
from meaningcloud_common import setRequestSource, isBlockingErrorType, insertInList

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
language = get_recipe_config().get("language")
topics = get_recipe_config().get("topics")
threshold = int(get_recipe_config().get("threshold", 100))
user_dictionary = get_recipe_config().get("user_dictionary", "")


# ==============================================================================
# AUXILIARY FUNCTIONS
# ==============================================================================

# Analyzes the text passed as a parameter
def analyzeText(text, language, threshold, tt, ud):
    global index_count
    print("Extracting topics for text #%s" % str(index_count))

    # this is where we are going to store our results
    topics = {
        "person": [],
        "organization": [],
        "location": [],
        "product": [],
        "id": [],
        "event": [],
        "other": [],
        "quantity": [],
    }

    try:
        # We are going to make a request to the Topics Extraction API
        request = meaningcloud.TopicsRequest(
            license_key,
            txt=text,
            lang=language,
            topicType=tt,
            server=server,
            otherparams={"ud": ud},
        )
        setRequestSource(request)
        response = meaningcloud.TopicsResponse(request.sendReq())

        if response.isSuccessful():
            if "e" in tt:
                entity_list = response.getEntities()
                if entity_list:
                    for entity in entity_list:
                        if int(response.getTopicRelevance(entity)) >= threshold:
                            first_node = response.getTypeFirstNode(
                                response.getOntoType(entity)
                            ).lower()
                            form = str(response.getTopicForm(entity))
                            insertInList(topics.get("other"), form) if topics.get(
                                first_node
                            ) is None else insertInList(topics.get(first_node), form)
            if "c" in tt:
                concept_list = response.getConcepts()
                if concept_list:
                    for concept in concept_list:
                        if int(response.getTopicRelevance(concept)) >= threshold:
                            first_node = response.getTypeFirstNode(
                                response.getOntoType(concept)
                            ).lower()
                            form = str(response.getTopicForm(concept))
                            insertInList(topics.get("other"), form) if topics.get(
                                first_node
                            ) is None else insertInList(topics.get(first_node), form)
            if "m" in tt:
                money_expression_list = response.getMoneyExpressions()
                if money_expression_list:
                    [
                        insertInList(
                            topics.get("quantity"), str(response.getTopicForm(money))
                        )
                        for money in money_expression_list
                    ]
            if "n" in tt:
                quantity_expression_list = response.getQuantityExpressions()
                if quantity_expression_list:
                    [
                        insertInList(
                            topics.get("quantity"), str(response.getTopicForm(quantity))
                        )
                        for quantity in quantity_expression_list
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
                    "Oops! The request to Topics Extraction for text #"
                    + str(index_count)
                    + " was not succesful: ("
                    + response.getStatusCode()
                    + ") "
                    + response.getStatusMsg()
                )
                topics = {
                    "person": "ERROR ("
                    + response.getStatusCode()
                    + "): "
                    + response.getStatusMsg(),
                    "organization": "",
                    "location": "",
                    "product": "",
                    "id": "",
                    "event": "",
                    "other": "",
                    "quantity": "",
                }

    except ValueError as e:
        raise ValueError(str(e))

    index_count += 1
    return pd.Series(topics)


# ==============================================================================
# MAIN FLOW
# ==============================================================================

if text_column is None or len(text_column) == 0:
    raise ValueError("You must specify the input text column.")

if topics is None or len(topics) == 0:
    raise ValueError("You must specify some topics to extract.")

if not input_dataset:
    raise ValueError("No input dataset specified!")

input_df = input_dataset.get_dataframe()

if text_column not in input_df:
    raise ValueError("The column configured does not exist in the data input!")

tt = "".join([topics[a] for a in range(len(topics))])
print(
    "Starting analysis for %d texts to extract '%s' in '%s'... "
    % (len(input_df), tt, language)
)


output_df = input_df

# main analysis
index_count = 1
label_list = [
    "person",
    "organization",
    "location",
    "product",
    "id",
    "event",
    "other",
    "quantity",
]
label_list = ["topic_" + l for l in label_list]
output_df[label_list] = input_df[text_column].apply(
    analyzeText, language=language, threshold=threshold, tt=tt, ud=user_dictionary
)


# write results
output_dataset.write_with_schema(output_df)
