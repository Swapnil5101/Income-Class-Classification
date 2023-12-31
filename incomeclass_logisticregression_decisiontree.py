# -*- coding: utf-8 -*-
"""incomeclass-logisticregression-decisiontree.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-8nV50W3t8RciWWoWJrGNHFDKC2qCuc5

## Introduction
This notebook is aimed to explore and gain insights from the "income-classification" dataset (more at link) and predict whether an individual has income higher than 50K.
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import seaborn as sb
import matplotlib.pyplot as plt
# %matplotlib inline
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn import metrics
import warnings
warnings.filterwarnings('ignore')

# import os
# for dirname, _, filenames in os.walk('/kaggle/input'):
#     for filename in filenames:
#         print(os.path.join(dirname, filename))

df = pd.read_csv('/content/income_evaluation.csv')
df.head(10)

"""## EDA"""

df.info()

# Check whether there is any null value
df.isna().sum()

# Check for duplicates
print("Number of duplicate values is", df.duplicated().sum())

df.loc[df.duplicated()].head(10)

# Remove the duplicate tuples
df.drop_duplicates(inplace=True)
df.shape

df.columns

"""So there's a problem in the dataset - **every 'object' type column name and string values start with a whitespace.**"""

# df.rename(columns={' workclass': 'workclass', ' fnlwgt': 'fnlwgt', ' education': 'education', ' education-num': 'education_num',
#        ' marital-status': 'marital_status', ' occupation': 'occupation', ' relationship': 'relationship', ' race': 'race',
#         ' sex': 'sex', ' capital-gain': 'capital_gain', ' capital-loss': 'capital_loss', ' hours-per-week': 'hours_per_week',
#         ' native-country': 'native_country', ' income': 'income'}, inplace=True)

df.columns = df.columns.str.replace(' ', '')
df.columns = df.columns.str.replace('-', '_')
df.columns

print(df['education'].unique())
print(df['education_num'].unique())

"""**finlwgt(final weight)**: This is the number of people the census believes the entry represents.

**education-num**: It seems like this is code number for different values in 'education' column. That is, it represents the same information as 'education' column.
"""

df.describe(include='all')

df['native_country'].value_counts()

"""**The data is majorly inclined towards persons who are native to USA.**

**One of the countries is (probably) not known in the survey(weird case) and it is represented by '?'.**
"""

df['education'].value_counts()

"""* **The mostly employed people are those who completed High School graduation.**
* **The least employed people are those who have only Preschool education.**

It is visualized in one of the below plots.
"""

df.head()

df['race'].value_counts()

# Race-wise income comparison
pd.crosstab(index=df['race'], columns=df['income']).plot(kind='bar', figsize=(8,4), grid=True)
plt.title("Race-wise income comparison")
plt.xlabel("Race")
plt.ylabel("Frequency")
plt.show()

"""Clearly, **white people are getting more opportunities as compared to others (in both income categories)**, a harsh reality of world. One can argue that this is because the whites are more in number as dataset participants, but it's still a fact."""

sb.distplot(df['age'])

"""* **Minimum age is 17 and maximum is 90. Average working age, in this dataset, is 38.585**
* **The plot for age is left skewed.**

### Percentage of people in an income category
"""

df['income'].value_counts()



"""* **Mostly have income <= 50k $**"""

income_class = df['income'].value_counts().index
class_val = df['income'].value_counts().values

plt.pie(class_val, labels=income_class, autopct='%1.2f%%', shadow=True)

"""**It can be clearly seen that more than 75% individuals in the sample are having income less than or equal to 50,000$(annual)**

### Categorical features' analysis

What and how many categorical features are there?
"""

cat_features = [feature for feature in df.columns if df[feature].dtypes == 'O']
cat_features

for feature in cat_features:
    print("The number of categories in '{}' are {}.".format(feature, len(df[feature].unique())))

"""#### Income scenerio and people count for 'education' column"""

df.groupby(['education', 'income']).size().reset_index().rename(columns={0:'#people'})

"""* **Maximum are High School graduates.**
* **Maximum number of people who have >50k $ annual income are those who got job after their Bachelor degree.**
* **No Preschool pass out has income >50K and this category people are least employed.**

These things are clearly visible in the below plots:
"""

plt.figure(figsize=(20, 8))
sb.histplot(data=df['education'], color='y')
plt.xlabel("Education")
plt.ylabel("Number of persons")
plt.show()

# Education levelwise income comparison
pd.crosstab(index=df['education'], columns=df['income']).plot(kind='bar', figsize=(20,6), color=['red', 'green'], grid=True)
plt.title("Number of Persons in income categories (Education levelwise)")
plt.xlabel("Education level")
plt.ylabel("Frequency")
plt.show()

# Genderwise income comparison
pd.crosstab(index=df['sex'], columns=df['income']).plot(kind='bar', figsize=(15,5), grid=True)
plt.title("Number of Persons in income categories (Male vs Female)")
plt.xlabel("Sex")
plt.ylabel("Frequency")
plt.show()

"""* **In both income categories, male individuals are higher in number (overall also higher in the whole collected sample.)**
* **In '>50K' income category, males are almost 6.5 times female individuals.**
"""

df['workclass'].value_counts()

"""* **one of the workclasses(with 1836 samples) is not named! It's represented by '?'**
* **Most prefered workclass(in this dataset) is Private.**
"""

df['occupation'].value_counts()

"""* **The top occupation(in terms of count) is 'Prof-specialty' and the least one is 'Armed-Forces'**
* **Here also one occupation is marked as '?'**

Let's rename/replace '?' in 'workclass' and 'occupation' columns by 'Unknown'.
"""

#Replace '?' by 'Unknown'
df['workclass'].replace({' ?':'Unknown'}, inplace=True)
df['occupation'].replace({' ?':'Unknown'}, inplace=True)

"""Similarly, 'native_country' column has also '?'"""

df['native_country'].replace({' ?':'Unknown'}, inplace=True)
df['native_country'].unique()

df.workclass.unique()

fig, axes = plt.subplots(2, 2, figsize=(20, 15))
axes = axes.flatten()
fig.suptitle("Relationship between categorical attributes and income")
cat_attrs = ['workclass', 'occupation', 'marital_status', 'relationship']

for ax, element in enumerate(cat_attrs):
    plt.legend(bbox_to_anchor=(1.2, 1.2), loc='upper right')
    sb.countplot(data=df, x='income', hue=element, alpha=0.7, ax=axes[ax], palette='dark')

"""1. **Workclass**
* Private jobs have topped in both income categories.
* This somehow also depicts that people are not hesitating in doing private rather than government jobs. Or another reason can be that number of job vacancies in government institutions are too less as compared to private companies, which forces people to grab or shift to private jobs.
2. **Occupation**
* In <=50K income category, highest number of people are in 'Adm-clerical' occupation followed by 'Craft-repair' and 'Other service'.
* In >50K income category, 'Exec-managerial' topped in terms of count, followed by 'Prof-specialty' occupation.
3. **Marital Status**
* Looks like unmarried persons(maybe fresh college passouts or ones with less experience) are highest in number in <=50K income category (most companies/organisations hunt such people).
* Married persons are getting more salaries (the most probable reason being that they have gained nice work experience).
* But those who are not in 'Never-married' category but fall in other(i.e., they might have some experience), are also getting less income(i.e., not >50K). The simple logic that can be drawn is that a married person has responsibilities of his/her family and that's what drives him/her more (in comparison to others) to work harder and getting promoted.
4. **Relationship**
* 'Not-in-family' persons are more in <=50K income category for the similar probable reason as in case of 'Never-married' marital status. Then followed by Husbands who keep their work life going (for themselves as well as for their family, usual case in any country).
* In >50K income category, Husbands topped, for the simple reason, again, that they have got work and life experiences and they have lots of responsibilities also.
* But surprisingly wives do not have the same case (neither in <=50K income nor in >50K income). The reason could be that the number of females in this income survey (or in the dataset) are quite less than males. Therefore, the visualization here is not depicting a closer real life picture of income scenerio, even after gender equality has become key concern in both social and work life.

### Outlier detection
"""

# age and hours-per-week
plt.figure(figsize=(15, 8))
sb.boxplot(data=df[['age', 'hours_per_week']], orient='h')

"""In 'age' column's boxplot, age>80 (approx.) entries are outliers. It's natural that people prefer to leave work life at such an age. Median age is around 38 years.

Lots of outliers can be seen in 'hour_per_week' column. Median is around 42 hours.
"""

# fnlwgt
plt.figure(figsize=(15, 6))
sb.boxplot(df['fnlwgt'], orient='h')

# capital_gain and capital_loss
plt.figure(figsize=(10, 5))
sb.boxplot(data=df[['capital_gain', 'capital_loss']], orient='h')

"""**'capital_gain' and 'capital_loss' columns are filled with outliers. Their 1st and 3rd quartiles are also 0.**

## Feature Engineering

Now work with a copy of the same dataframe
"""

df2 = df.copy()

"""### Handling rare categorical values

Some of the categorical values (for example 'Scotland', 'Holand-Netherlands' in 'native_country' column) are relatively very less in number. So they will not create much impact on output whether we include them or not. So let's take into consideration only those values which are greater than 0.5%, rest all we will consider as single categorical value (let's say rare_cat) for each categorical column.
"""

for feature in cat_features:
    temp = df2.groupby(feature)['income'].count()/len(df2)
    temp_df2 = temp[temp>0.005].index
    df2[feature] = np.where(df2[feature].isin(temp_df2), df2[feature], 'rare_cat')

df2.head(10)

"""### Categorical to numerical encoding"""

for feature in cat_features:
    feature_lst_ordered = sorted(list(df2[feature].unique()))
    encodings = {k:i for i,k in enumerate(feature_lst_ordered)}
    df2[feature] = df2[feature].map(encodings)

"""Since 'education' and 'education_num' represent the same thing, drop the 'education' column."""

df2.drop('education', axis=1, inplace=True)

df2.head()

df.head()

"""**Correlation Matrix**"""

corr = df2.corr()
matrix = np.triu(corr)
plt.figure(figsize=(8, 8))
sb.heatmap(data=corr, vmin=-1, vmax=1, cmap='binary', fmt='.1g', annot=True, mask=matrix)
plt.title("Correlation Matrix")
plt.show()

"""Seems like most of the features are not much correlated with 'income'!

It's surprising that workclass and occupation are very less related to income!

### Removing outliers
"""

df2.describe().T

"""**We can see from correlation matrix that 'capital_gain' and 'capital_loss' columns have 'relatively' stronger correlation. So we should not drop them.**

But we must have a look at the entries where capital_gain is nearly 100000.
"""

df2.loc[df2['capital_gain']==99999]

"""All these people have income >50K. And there are 159 such entries. We must retain these entries because we can always find a few such sections in most of the societies or countries."""

df2.shape

# In case of 'age', it can be seen from above boxplot that entries corresponding to age>=80 are outliers.
df2 = df2.loc[df2['age']<80]

# For 'hours_per_week' column
Q3 = 45
Q1 = 40
IQR = 45-40
lf = Q1-1.5*IQR
uf = Q3+1.5*IQR
df2 = df2.loc[(df2['hours_per_week']>=lf) & (df2['hours_per_week']<=uf)]

"""In the dataset we initialy had 32537 rows (after removing duplicates). Let's see how much are left after removing the outliers of these two columns."""

df2.shape

"""Thousands of outliers were present in these 2 columns!

## Feature Scaling and splitting dataset

'fnlwgt' column is very less correlated to income. So retaining or dropping it will not harm model's accuracy.
"""

X = df2.drop(columns=['income'])
# X2 = df2.drop(columns=['income', 'fnlwgt'])
y = df2['income']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

"""Let's first consider **Normalisation (or MinMaxScalar)**. But note that in normalisation outliers will also be scaled in between 0 & 1, and will be considered in training."""

# Scaling
scaler = MinMaxScaler()
X_train_norm = X_train.copy()
X_test_norm = X_test.copy()
# scaler.fit_transform(X_train) is a numpy array so it needs to be converted into dataframe. Similarly for X_test
X_train_norm = pd.DataFrame(scaler.fit_transform(X_train_norm), index=X_train_norm.index, columns=X_train_norm.columns)
X_test_norm = pd.DataFrame(scaler.transform(X_test_norm), index=X_test_norm.index, columns=X_test_norm.columns)

X_test_norm.head()

"""Now, let's consider **Standardization**."""

std_scalar = StandardScaler()
X_train_s = X_train.copy()
X_test_s = X_test.copy()
X_train_s = pd.DataFrame(scaler.fit_transform(X_train_s), index=X_train_s.index, columns=X_train_s.columns)
X_test_s = pd.DataFrame(scaler.transform(X_test_s), index=X_test_s.index, columns=X_test_s.columns)

"""## Model building and Predictions

### Logistic Regression model (from scratch)
"""

y_train_copy = y_train.to_numpy()
y_test_copy = y_test.to_numpy()

y_train_copy.shape

y_train_copy = y_train_copy.reshape((y_train.shape[0], 1))
y_test_copy = y_test_copy.reshape((y_test.shape[0], 1))

# Sigmoid function
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# Initialize the weights and bias
def initialize_parameters(n):
    w = np.ones((n, 1))       # n = no. of features
    b = 0
    return w, b

# Forward propagation
def forward_prop(X_train, w, b):
    z = np.dot(X_train, w) + b
    H = sigmoid(z)               # Hypothesis
    return H

# Compute the cost (binary cross-entropy)
def compute_cost(H, y_train_copy):
    m = len(y_train_copy)
#     cost = -1/m * np.sum(y_train_copy.T * np.log(H) + (1 - y_train_copy).T * np.log(1 - H))
    cost = -1/m * np.sum(y_train_copy * np.log(H) + (1 - y_train_copy) * np.log(1 - H))
    return cost

# One step of gradient descent using backward propagation
def back_prop(X_train, y_train_copy, H):
    m = len(y_train_copy)
    dw = 1/m * np.dot(X_train.T, (H - y_train_copy))
    db = 1/m * np.sum(H - y_train_copy)
    return dw, db

# Update the weights and bias
def update_parameters(w, b, dw, db, alpha):
    w = w - alpha * dw
    b = b - alpha * db
    return w, b

# Train the logistic regression model (with learning rate = alpha)
def logistic_regression(X_train, y_train_copy, num_iterations, alpha):
    n = X_train.shape[1]
    w, b = initialize_parameters(n)

    for i in range(num_iterations):
        H = forward_prop(X_train, w, b)
        cost = compute_cost(H, y_train_copy)
        dw, db = back_prop(X_train, y_train_copy, H)
        w, b = update_parameters(w, b, dw, db, alpha)

        if i % 100 == 0:
            print("Iteration {}: Cost = {}".format(i, cost))

    return w, b

# Make predictions using the trained model
def predict(X_train, w, b):
    A = forward_prop(X_train, w, b)
    preds = (A > 0.5).astype(int)
    return preds

# Start training and grab the parameters
num_iterations = 1000
alpha = 0.01
w, b = logistic_regression(X_train_s, y_train_copy, num_iterations, alpha)

preds = predict(X_test_s, w, b)
print("Prediction on test data using Logistic Regression(from scratch):", preds)

LR_accuracy = metrics.accuracy_score(y_test, preds)
print("Accuracy of LR model:", LR_accuracy)

"""### Model using sklearn library"""

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

def model_scores(standardized=False):
    acc_scores = []
    predictions = []

    for model in Models:
        if(standardized):
            X_tn = X_train_s
            X_tt = X_test_s

        else:                            # Normalized
            X_tn = X_train_norm
            X_tt = X_test_norm

        M = model.fit(X_tn, y_train)
        y_pred = M.predict(X_tt)
        predictions.append(y_pred)
        print("Prediction of {} model on test data is {}.".format(model, y_pred))

        accuracy = metrics.accuracy_score(y_test, y_pred)

        acc_scores.append([M, accuracy, standardized])

    return acc_scores, predictions

Models = [LogisticRegression(solver='liblinear'),
          DecisionTreeClassifier()]

"""### Predictions, Accuracy and Confusion matrix

When Normalization is used:
"""

acc_scores_norm, pred_norm = model_scores()

"""When Standardization is used:"""

acc_scores_std, pred_std = model_scores(standardized=True)

models_df = pd.DataFrame(data=acc_scores_norm, columns=['Model', 'Accuracy', 'Standardized'])
models_df = pd.concat([models_df, pd.DataFrame(data=acc_scores_std, columns=['Model', 'Accuracy', 'Standardized'])],
                      ignore_index=True)

models_df.sort_values(by='Accuracy', ascending=False).reset_index(inplace=True)

models_df

"""Whether you standardize data or not, logistic regression model will give you almost the same accuracy. Similar is the case with Normalization.

**So in case of Logistic Regression, Decision Trees, Random Forest classifiers, standardizing data is not a good way (though it will not harm model's accuracy). Model will give you same accuracy even without standardization.**

**Here both the models(Logistic regression and Decision Tree) are giving almost the same accuracy, with Logistic having a little bit higher accuracy ~ 82%**
"""

conf_mat = metrics.confusion_matrix(y_test, pred_norm[0])
fig, ax = plt.subplots(figsize=(3,3))
sb.heatmap(conf_mat, cmap='copper', linecolor='gray', linewidths=0.5, fmt=".1f", annot=True, ax=ax)
plt.title("Confusion Matrix for Logistic Regression model")
plt.xlabel("y_predicted")
plt.ylabel("True y")
plt.show()

"""**The model needs some investigation. For income >50K, more values in test dataset are wrongly predicted by the model (i.e., false negatives are more in number in confusion matrix when our aim is to check whether income is >50K)**"""

conf_mat = metrics.confusion_matrix(y_test, pred_norm[1])
fig, ax = plt.subplots(figsize=(3, 3))
sb.heatmap(conf_mat, cmap='cubehelix', linecolor='gray', linewidths=0.5, fmt=".1f", annot=True, ax=ax)
plt.title("Confusion Matrix for Decision Tree model")
plt.xlabel("y_predicted")
plt.ylabel("True y")
plt.show()

"""Here is some relaxation in bothering about false negatives and false positives.

## Summary

* **Most of the people have income <=50k dollars per anum.**
* **The Logistic Regression model built from scratch is giving accuracy close to the one built using sklearn library (that's good).**
* **Both Logistic and DT models are giving almost the same accuracy (~ 80 - 82 %).**
"""