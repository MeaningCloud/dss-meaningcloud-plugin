# MeaningCloud Plugin

This plugin provides a connector to several MeaningCloud APIS to allow you to integrate its Text Analytics functionality in your Dataiku datasets. [MeaningCloud](https://www.meaningcloud.com/) is a cloud-based text analytics service that, through APIs, allows you to extract meaning from all kinds of unstructured content: social conversation, articles, documents...

The different APIs provide easy access to many NLP tasks such as automatic classification, sentiment analysis, topic extraction, etc. To be able to use the service, you just have to [log into MeaningCloud](https://www.meaningcloud.com/developer/login) (by registering or using other services to log in), and you will receive a license key associated to a basic Free plan.

You can read more about the plans and the features available [here](https://www.meaningcloud.com/products/pricing).

With this plugin, you can extract the following information from a text:

- Analyze the sentiment polarity, subjectivity, irony and emotional agreement ([Sentiment Analysis API](https://www.meaningcloud.com/developer/sentiment-analysis))
- Extract entities, keywords (concepts) and more organized by their semantic type (organization, person, location, etc.)([Topics Extraction API](https://www.meaningcloud.com/developer/topics-extraction))
- Detect its dominant language ([Language Identification API](https://www.meaningcloud.com/developer/language-identification))
- Extract an automatic summary ([Summarization API](https://www.meaningcloud.com/developer/summarization))
- Assign one or more categories according to predefined taxonomies such as IAB, or according to your own taxonomy ([Deep Categorization API](https://www.meaningcloud.com/developer/deep-categorization))

All these analyses are included as Dataiku recipes.


# Getting started

You only need two things:

- Install the [plugin](https://academy.dataiku.com/latest/tutorial/plugins/index.html) in Dataiku
- [Create an account](https://www.meaningcloud.com/developer/login) in MeaningCloud (if you don't have one already) to obtain your license key.
- (Optional) Request access to any of our [language](https://www.meaningcloud.com/developer/documentation/language-packs) or [vertical packs](https://www.meaningcloud.com/developer/documentation/vertical-packs) if you want to use the resources included in them.

Once you have this, you only need to add your license key either in the Settings section of the plugin or in the Configuration section of the recipe you want to use.

