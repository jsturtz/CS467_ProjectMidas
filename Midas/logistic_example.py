# Logistic Regression

# Importing the libraries
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import dask.dataframe as dk
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from matplotlib.colors import ListedColormap
from matplotlib.colors import ListedColormap

path = "../data/other_data/"
dataset = pd.read_csv(path + 'dev_train_top1000.csv')

# separating columns by dependent variable versus features
Y_label = "isFraud"               

# to identify columns that have numeric data
numerics              = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
X_numerical_feat      = dataset.select_dtypes(include=numerics).drop(Y_label, 1).values  # make sure to ignore dependent variable
X_categorical_feat    = dataset.select_dtypes(exclude=numerics).values

# Replace all missing categorical data with string that says 'missing_value'
imputer = SimpleImputer(missing_values = np.nan, strategy = 'constant')
X_categorical_feat = imputer.fit_transform(X_categorical_feat)

# Replace all missing numerical data with mean
imputer = SimpleImputer(missing_values = np.nan, strategy = 'mean')
X_numerical_feat = imputer.fit_transform(X_numerical_feat)

# Encode categorical variables
labelencoder  = LabelEncoder()
onehotencoder = OneHotEncoder()

# I hate this code and would love to figure out how to not be a dumbass about this
for i in range(len(X_categorical_feat[0])):
    X_categorical_feat[:, i] = labelencoder.fit_transform(X_categorical_feat[:, i])

X_categorical_feat = onehotencoder.fit_transform(X_categorical_feat).toarray()

# recombine numerical with encoded categorical
X = np.hstack((X_numerical_feat, X_categorical_feat))   # recombined categorical features with numerical
Y = dataset.loc[:, Y_label].values                      # dependent variable values are easy

# Logistic Regression

# # Splitting the dataset into the Training set and Test set
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.25, random_state = 0)

# # Feature Scaling
sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# Fitting Logistic Regression to the Training set
classifier = LogisticRegression(random_state = 0)
classifier.fit(X_train, Y_train)

# Predicting the Test set results
Y_pred = classifier.predict(X_test)
print(accuracy_score(Y_test, Y_pred))


# this stuff is borrowed from somewhere else but it needs to be refactored for my purposes

# # Making the Confusion Matrix
# cm = confusion_matrix(Y_test, Y_pred)


## Visualising the Training set results 
#X_set, Y_set = X_train, Y_train
#X1, X2 = np.meshgrid(np.arange(start = X_set[:, 0].min() - 1, stop = X_set[:, 0].max() + 1, step = 0.01),
#                     np.arange(start = X_set[:, 1].min() - 1, stop = X_set[:, 1].max() + 1, step = 0.01))
#plt.contourf(X1, X2, classifier.predict(np.array([X1.ravel(), X2.ravel()]).T).reshape(X1.shape),
#             alpha = 0.75, cmap = ListedColormap(('red', 'green')))
#plt.xlim(X1.min(), X1.max())
#plt.ylim(X2.min(), X2.max())
#for i, j in enumerate(np.unique(Y_set)):
#    plt.scatter(X_set[Y_set == j, 0], X_set[Y_set == j, 1],
#                c = ListedColormap(('red', 'green'))(i), label = j)
#plt.title('Logistic Regression (Training set)')
#plt.xlabel('Age')
#plt.ylabel('Estimated Salary')
#plt.legend()
#plt.show()
#
## Visualising the Test set results
#X_set, Y_set = X_test, Y_test
#X1, X2 = np.meshgrid(np.arange(start = X_set[:, 0].min() - 1, stop = X_set[:, 0].max() + 1, step = 0.01),
#                     np.arange(start = X_set[:, 1].min() - 1, stop = X_set[:, 1].max() + 1, step = 0.01))
#plt.contourf(X1, X2, classifier.predict(np.array([X1.ravel(), X2.ravel()]).T).reshape(X1.shape),
#             alpha = 0.75, cmap = ListedColormap(('red', 'green')))
#plt.xlim(X1.min(), X1.max())
#plt.ylim(X2.min(), X2.max())
#for i, j in enumerate(np.unique(Y_set)):
#    plt.scatter(X_set[Y_set == j, 0], X_set[Y_set == j, 1],
#                c = ListedColormap(('red', 'green'))(i), label = j)
#plt.title('Logistic Regression (Test set)')
#plt.xlabel('Age')
#plt.ylabel('Estimated Salary')
#plt.legend()
#plt.show()
