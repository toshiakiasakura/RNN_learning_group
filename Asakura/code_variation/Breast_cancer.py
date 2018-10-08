
# coding: utf-8

# Attribute Information:
# 
#     1) ID number
#     2) Diagnosis (M = malignant, B = benign)
# 
# -3-32.Ten real-valued features are computed for each cell nucleus:
# 
#     a) radius (mean of distances from center to points on the perimeter)
#     b) texture (standard deviation of gray-scale values)
#     c) perimeter
#     d) area
#     e) smoothness (local variation in radius lengths)
#     f) compactness (perimeter^2 / area - 1.0)
#     g). concavity (severity of concave portions of the contour)
#     h). concave points (number of concave portions of the contour)
#     i). symmetry
#     j). fractal dimension ("coastline approximation" - 1)
# 
# convave ->凹み
# 
# The mean, standard error and "worst" or largest (mean of the three largest values) of these features were computed for each image, resulting in 30 features. For instance, field 3 is Mean Radius, field 13 is Radius SE, field 23 is Worst Radius.
# 
# For this analysis, as a guide to predictive analysis I followed the instructions and discussion on "A Complete Tutorial on Tree Based Modeling from Scratch (in R & Python)" at Analytics Vidhya.

# In[293]:


import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# keeps the plots in one place. calls image as static pngs
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt # side-stepping mpl backend
import matplotlib.gridspec as gridspec # subplots
import mpld3 as mpl

#Import models from scikit learn module:
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import KFold   #For K-fold cross validation
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn import metrics


import graphviz
import pydot


# In[232]:


df = pd.read_csv("data.csv",header = 0)
df


# In[233]:


df.drop('id',axis=1,inplace=True)
df.drop('Unnamed: 32',axis=1,inplace=True)
# size of the dataframe
len(df)


# In[234]:


df.diagnosis.unique()


# In[235]:


df['diagnosis'] = df['diagnosis'].map({'M':1,'B':0})
df.head()


# In[236]:


df.describe()  # basic statistic #, mean,sd ,min ,25,75,max points. 


# In[237]:


df.describe()
plt.hist(df['diagnosis'])
plt.title('Diagnosis (M=1 , B=0)')
plt.show()


# In[238]:


features_name = df.columns[1:11]
dfM = df[df["diagnosis"] == 1]
dfB = df[df["diagnosis"] == 0]


# In[239]:


#stack the data 
plt.rcParams.update({"font.size":8})
fig, axes = plt.subplots(nrows=5,ncols=2,figsize=(10,18))

axes = axes.ravel() # 5*2 list data
for idx,ax in enumerate(axes):
    ax.figure
    binwidth = (max(df[features_name[idx]]) - min(df[features_name[idx]]))/50
    ax.hist([dfM[features_name[idx]],dfB[features_name[idx]]],
        bins=np.arange(min(df[features_name[idx]]) ,max(df[features_name[idx]])+binwidth,binwidth), 
        alpha = 0.5,stacked=True, normed= True,label=["M","B"],color=["r","g"])
    ax.legend(loc="upper right")
    ax.set_title(features_name[idx])
plt.tight_layout()
plt.show()



# mean values of cell radius, perimeter, area, compactness, concavity and concave points can be used 
# in classification of the cancer. 
# 

# going to bulid model 

# In[248]:


predictor_var = ['radius_mean','perimeter_mean','area_mean','compactness_mean','concave points_mean']
df[predictor_var].head()
print (int( len(df)/2 ) )


# In[294]:


#Generic function for making a classification model and accessing the performance. 
# From AnalyticsVidhya tutorial
def classification_model(model, data, predictors, outcome):
  #Fit the model:
  model.fit(data[predictors][:int(len(df)/2)] ,data[outcome][:int(len(df)/2)])
  
  #Make predictions on training set:
  predictions = model.predict(data[predictors][int(len(df)/2): ])
  
  #Print accuracy
  accuracy = metrics.accuracy_score(predictions,data[outcome][int(len(df)/2): ])
  print("Accuracy : %s" % "{0:.3%}".format(accuracy))

  #Perform k-fold cross-validation with 5 folds
  kf = KFold(data.shape[0], n_folds=5)
  error = []
  for train, test in kf:
    # Filter training data
    train_predictors = (data[predictors].iloc[train,:])
        # .iloc means row number,  .loc
    
    # The target we're using to train the algorithm.
    train_target = data[outcome].iloc[train]
    
    # Training the algorithm using the predictors and target.
    model.fit(train_predictors, train_target)
    
    #Record error from each cross-validation run
    error.append(model.score(data[predictors].iloc[test,:], data[outcome].iloc[test]))
    
    print("Cross-Validation Score : %s" % "{0:.3%}".format(np.mean(error)))
    
  #Fit the model again so that it can be refered outside the function:
  model.fit(data[predictors],data[outcome]) 


# Logistic Regression model

# In[254]:


predictor_var = ['radius_mean','perimeter_mean','area_mean','compactness_mean','concave points_mean']
outcome_var='diagnosis'
model=LogisticRegression()
classification_model(model,df,predictor_var,outcome_var)


# In[295]:


# try to check using one variables 
predictor_var = ['radius_mean']
model=LogisticRegression()
classification_model(model,df,predictor_var,outcome_var)


# Decision Tree model

# In[296]:


predictor_var = ['radius_mean','perimeter_mean','area_mean','compactness_mean','concave points_mean']
model = DecisionTreeClassifier()
classification_model(model,df,predictor_var,outcome_var)


# In[257]:


predictor_var = ['radius_mean']
model = DecisionTreeClassifier()
classification_model(model,df,predictor_var,outcome_var)


# In[258]:


# show tree as graph
export_graphviz(model,out_file="tree.dot",class_names=["malignant","benign"],
                feature_names=predictor_var,impurity=False,filled=True)
with open("tree.dot") as f:
    dot_graph = f.read()
graphviz.Source(dot_graph)
(graph,) = pydot.graph_from_dot_file("tree.dot")
graph.write_png("tree.png")


# Random Forest

# In[308]:


predictor_var = features_name
model = RandomForestClassifier(n_estimators=100,min_samples_split=25, max_depth=7, max_features=3)
classification_model(model, df,predictor_var,outcome_var)


# In[309]:


featimp = pd.Series(model.feature_importances_, index=predictor_var).sort_values(ascending=False)
print(featimp)


# In[318]:


from pylab import rcParams
rcParams['figure.figsize'] = 7,5

a = model.feature_importances_.argsort()
model.feature_importances_[a]

# make the graph

plt.barh(range(len(a)) ,model.feature_importances_[a],align="center")
plt.yticks(np.arange(len(a)),features_name)
plt.xlabel = "Importance Feature"
plt.ylabel = "Feature"
plt.show()


# In[262]:


# Using top 5 features
predictor_var = ['concave points_mean','area_mean','radius_mean','perimeter_mean','concavity_mean',]
model = RandomForestClassifier(n_estimators=100, min_samples_split=25, max_depth=7, max_features=2)
classification_model(model,df,predictor_var,outcome_var)

