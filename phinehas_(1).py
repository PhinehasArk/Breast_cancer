# -*- coding: utf-8 -*-
"""PHINEHAS (1).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17OsjDiQacZNsd2FC6-IqGutFvSoC3eDM

# IMPORTING OF LIBRARIES
"""

!pip install shap # model interpretation
!pip install dataprep # data exploration

# Commented out IPython magic to ensure Python compatibility.

# Packages to load and preprocess data
import numpy as np
import pandas as pd
import io

# Packages to visualise and explore data
import seaborn as sns
sns.set_style("whitegrid")
import matplotlib.pyplot as plt
# from dataprep.eda import plot, create_report
from dataprep.eda import plot, create_report, plot_missing, plot_correlation

# Packages to prepare data for ML  
from sklearn.preprocessing import OrdinalEncoder
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn import metrics
from mlxtend.plotting import plot_confusion_matrix
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegressionCV
from sklearn.svm import SVC
from sklearn import neighbors
from sklearn.model_selection import RandomizedSearchCV
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
# %matplotlib inline

# Package to interpret data
import shap

# Package to save the chosen model
import pickle

"""   # LOADING OF DATASET"""

# Connect to google drive 
from google.colab import drive
drive.mount('/content/drive')

df = pd.read_excel(('/content/drive/MyDrive/Project/finaldata.xlsx'))
# Dataset is now stored in a Pandas Dataframe

"""# DATA PRE-PROCESSING"""

df.head() # Head of the dataset n= 5

# converting original values to absoluve values 
df['UMAMP_X'] = df['UMAMP_X'].abs()
df['UMAP_Y'] = df['UMAP_Y'].abs()
df['relative_expression'] = df['relative_expression'].abs()

df.tail() # Tail of the data set n =5

df = df.fillna(df.mean()) # fill NAN with mean

df.info()

df.shape

df.drop(['cell_line','cell_id'], axis=1, inplace=True)

df.count()

df.describe().transpose()

df.isnull()

df.isna().sum()

df.describe()

"""# EXPLORATORY DATA ANALYSIS """

report = create_report(df, title='BC classification by subtypes') # EDA using create report

report

report.save('/content/drive/MyDrive/Project/EDA_BCSubtype_prediction.html')

fig = plt.figure(figsize=(5,5), dpi=200)
sns.boxplot(x="BC_type", y="cluster", data=df).set(title="Analysis of cluster on BC Subtypes types", xlabel="BC Types")
plt.show()

"""# MACHINE LEARNING

# DATA SCALING
"""

#Normalize the value of X
x =  df.drop("BC_type", axis=1)

# create a MinMaxScaler object
scaler = MinMaxScaler()

# fit the scaler object to your data and transform it
norm_df = scaler.fit_transform(x)

# convert the normalized data to a pandas DataFrame
norm_df = pd.DataFrame(norm_df, columns=x.columns)

# show the first 5 rows of the normalized data
norm_df.head()

"""## TRAIN, TEST , and SPLIT DATASET"""

X = norm_df
y = df['BC_type']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2) # 80 percent for training  and 20 for percent testing

"""
# RANDOM FOREST CLASSIFICATION"""

# sc = StandardScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# Run model 


randomF = RandomForestClassifier(n_estimators = 10, criterion = 'entropy', random_state = 42)
randomF.fit(X_train, y_train)
randomF_pred = randomF.predict(X_test)
X_train.shape, X_test.shape

print(classification_report(y_test, randomF_pred))

param_grid = {
    'n_estimators': [25, 50, 100, 150],
    'max_features': ['sqrt', 'log2', None],
    'max_depth': [3, 6, 9],
    'max_leaf_nodes': [3, 6, 9],
}

# parameter tuning
grid_search = GridSearchCV(RandomForestClassifier(),
                           param_grid=param_grid)
grid_search.fit(X_train, y_train)
print(grid_search.best_estimator_)

# updating of model
new_random = RandomForestClassifier(max_depth=9,
                                      max_features='log2',
                                      max_leaf_nodes=9,
                                      n_estimators=100)
new_random.fit(X_train, y_train)
y_pred_rand = new_random.predict(X_test)
print(classification_report(y_pred_rand, y_test))

randomF_acc = accuracy_score(y_test, y_pred_rand)

randomF_acc

model_acc_list  = []
model_acc_list.append(randomF_acc * 100)

model_acc_list

cnf_matrixrf = metrics.confusion_matrix(y_test, y_pred_rand)

p = sns.heatmap(pd.DataFrame(cnf_matrixrf), annot=True, cmap="YlGnBu" ,fmt='g')
plt.title('Confusion matrix', y=1.1)
plt.ylabel('Actual label')
plt.xlabel('Predicted label')

"""# K-Nearest Neighbors Algorithm"""

# run of model
scaler = StandardScaler()
scaled_X_train = scaler.fit_transform(X_train)
scaled_X_test = scaler.transform(X_test)
knn = KNeighborsClassifier(n_neighbors=1)
knn.fit(scaled_X_train, y_train)

# calculating the accuracy of models with different values of k
mean_acc = np.zeros(20)
for i in range(1,21):
    #Train Model and Predict  
    knn = KNeighborsClassifier(n_neighbors = i).fit(X_train,y_train)
    yhat= knn.predict(X_test)
    mean_acc[i-1] = metrics.accuracy_score(y_test, yhat)

mean_acc

loc = np.arange(1,21,step=1.0)
plt.figure(figsize = (6, 5))
plt.plot(range(1,21), mean_acc)
plt.xticks(loc)
plt.xlabel('Number of Neighbors ')
plt.ylabel('Accuracy')
plt.show()

grid_params = { 'n_neighbors' : [5,7,9,11,13,15],
               'weights' : ['uniform','distance'],
               'metric' : ['minkowski','euclidean','manhattan']}

gs = GridSearchCV(KNeighborsClassifier(), grid_params, verbose = 1, cv=6, n_jobs = -1)

knng_res = gs.fit(X_train, y_train)

knng_res.best_score_

knng_res.best_params_ # hyperparameter with best score

# use the best hyperparameters
knn = KNeighborsClassifier(n_neighbors = 5, weights = 'distance',algorithm = 'brute',metric = 'manhattan')
knn.fit(X_train, y_train)

# get a prediction
y_hat = knn.predict(X_train)
y_knn = knn.predict(X_test)

# model evaluation
print('Training set accuracy: ', metrics.accuracy_score(y_train, y_hat))
print('Test set accuracy: ',metrics.accuracy_score(y_test, y_knn))

knn_pred = knn.predict(X_test)
print(classification_report(y_test, y_knn))

from sklearn.model_selection import cross_val_score
scores = cross_val_score(knn, X, y, cv =6)

print('cross val scores: ',np.mean(scores))

knn_acc = accuracy_score(y_test, y_knn)

knn_acc

model_acc_list.append(knn_acc * 100)

model_acc_list

"""# Logistic regression multiclass classification"""

scaler = StandardScaler()
scaled_X_train = scaler.fit_transform(X_train)
scaled_X_test = scaler.transform(X_test)
lg = LogisticRegressionCV()
lg.fit(scaled_X_train, y_train)

lg_pred = lg.predict(scaled_X_test)

print(classification_report(y_test, lg_pred))

lg_acc = accuracy_score(y_test, lg_pred)
model_acc_list.append(lg_acc * 100)

lg_acc

"""# Support Vector Machine"""

scaled_X_train = scaler.fit_transform(X_train)
scaled_X_test = scaler.transform(X_test)
svc = SVC()

svc.fit(X_train,y_train)

svcy_pred=svc.predict(X_test)

# compute and print accuracy score
print('Model accuracy score with default hyperparameters: {0:0.4f}'. format(accuracy_score(y_test, svcy_pred)))

param_grid = {'C': [0.001, 0.01, 0.1, 0.5, 1], 'gamma': ['scale', 'auto']}

grid = GridSearchCV(SVC(),param_grid,refit=True,verbose=2)
grid.fit(X_train,y_train)

grid.best_params_

svc_pred = grid.predict(scaled_X_test)
print(classification_report(y_test, svcy_pred))

svc_acc = accuracy_score(y_test, svcy_pred)
model_acc_list.append(svc_acc * 100)

svc_acc

model_acc_list

"""# LIST OF MODELS"""

model_list = ["Random Forest", "KNearestNeighbors", "LogisticRegression","SVC"]

model_list

model_acc_list

print(randomF_acc)
print(knn_acc)
print(lg_acc)
print(svc_acc)

sns.set_style("whitegrid")
sns.color_palette("Paired")
plt.figure(figsize=(8,8), dpi=60)
ax = sns.barplot(x=model_list, y=model_acc_list)
plt.title("Accuracy of Models")
plt.xlabel('Classification Models')
plt.ylabel("Accuracy of Classification Model")
for i in ax.patches:
    width, height = i.get_width(), i.get_height()
    x, y = i.get_xy() 
    ax.annotate(f'{round(height,2)}%', (x + width/2, y + height*1.02), ha='center')
plt.show()

"""# choosing of final model"""

final_model = knn.fit(X_train, y_train)

pickle.dump(final_model, open('final_model.pkl', 'wb'))

"""## Saving the model """

filename = 'finalized_model.sav'
pickle.dump(final_model, open(filename, 'wb'))

"""## Loading of the model"""

loaded_model = pickle.load(open(filename, 'rb'))
result = loaded_model.score(X_test, y_test)

"""## Testing the saved model on the testing dataset"""

pickled_model = pickle.load(open('final_model.pkl', 'rb'))
pickled_model.predict(X_test)



"""## Testing the model on a new set of data other than the one for the project

## Importing of dataset
"""

TS = pd.read_excel(('/content/drive/MyDrive/Project/pt.xlsx'))
# Dataset is now stored in a Pandas Dataframe

TS # This dataset has not been given the target variable

pickled_model = pickle.load(open('final_model.pkl', 'rb'))
pickled_model.predict(TS)

"""# The model has now work on a new set of data other than the dataset for the project.

### Thank you !
"""

