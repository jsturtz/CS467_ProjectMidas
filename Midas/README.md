# Midas

Machine Learning Pipeline Project

# Pipeline Steps

## Import

Training data is imported into a raw data collection. 

1. A checksum value is generated for the imported training data file such there is a unique identifier for each training dataset.
1. The data is minimally processed into a dataframe in order to retain the data as close as possible to its original form.
1. The data in dataframe format is loaded into an unstructured database, with the checksum value as its unique key.

## Analysis/Preprocessing

Datasets are summarized in table and graphical form for user evaluation. 

1. Data is exported from the raw data collection into a dataframe.
1. Evaluation of the data in the dataframe yields a new dataframe with summary values presented for each column in the dataframe. For numeric values, these are the ranges as well as aggregate evaluations like mean, mode, range. For categorical values, these are a compilation of most frequent values and the types of values observed. For both numerical and categorical types, a count of missing values is provided.
1. These representations are also provided in graphical form, presenting the user with summaries of aggregate transformations for numeric values and counts of categorical values.

## Cleaning

Data is cleaned in order to fix or remove records that do not fit required parameters for model training.

1. Records that are expected to have values such that the absence of values represents an invalid record are removed.
1. Records with numeric values that are outside of 1.5 inner quartile ranges of the lower and upper bounds are removed.
1. Numeric features are standardized such that the mean = 0 and variance is 1.
1. Missing values are imputed. With numeric values, aggregation results are used. Generally, this is a simple computation such as the mean or the median. In other cases, this may be a computed value using Bayesian Inference methods. 
1. For categorical values, this will generally be marking the record with a "missing" value or population of the record using the most common value.
1. PCA is performed on the dataset to offer the option of reductionality reduction.
1. The resulting dataset is saved to the structured database with the same unique identifier.

## Model Selection/Training

Data is split into train and test sets. A chosen algorithm is trained and performance metrics are provided.

1. Training data is split into train and test sets. By default, this is 70/30.
1. The underlying data may be manipulated to conform to requirements of the chosen algorithm. This may include categorical/label encoding, normalization, and further imputation.
1. Training results are stored in a table. A record contains a checksum for tha training data, a checksum of the pickled model, the name of the algorithm used, and a confusion matrix. Checksums for the training data and the pickled model act as keys for the accessing the raw data and the trained model.
1. The unique model id is provided to the user. This can be used to view the results or access the model for running the model on new data.


## Run Model

New data that matches the dataset in shape and datatypes is provided.

1. Given a trained model, identified by the unique model id, and new data, the data undergoes the same cleaning process the training data used.
1. The trained model unpickled and run against the new data.
1. A table with predictions labeled by index is provided to the user, corresponding to the index order provided by the user.