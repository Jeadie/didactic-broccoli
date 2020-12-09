import pandas as pd 
import numpy as np
import scipy as scipy
import sklearn 
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier


df = pd.read_csv("data.csv", sep=',', header=1)
df["home_points"] = df["Home Score"] - df["Away Score"]
print(df["home_win"].shape)
print(df["Away Odds"].shape)
x = np.transpose(np.stack([df["Away Odds"].values, df["Home Odds"].values]))

y = df["home_win"].values

# Remove bad values

print(np.logical_not(np.isnan(x)[:, 0]).shape)
y = y[np.logical_not(np.isnan(x)[:, 0])]
x = x[np.logical_not(np.isnan(x)[:, 0])]
assert x.shape[0] == y.shape[0]
print(f"There are {x.shape[0]} inputs.")

x, x_norm =  sklearn.preprocessing.normalize(x)
print(x_norm)

model = MLPRegressor(hidden_layer_sizes=(20, 10), activation="relu", solver="adam", alpha=0.0001, batch_size="auto", learning_rate="constant", learning_rate_init=0.001)

x_train, y_train = x[0:1600, :], y[0:1600]
x_test, y_test = x[1600:, :], y[1600:]
clf.fit(x_train, y_train)

train_accuracy = clf.score(x_train, y_train) 
test_accuracy = clf.score(x_test, y_test)

print(f"Accuracy on Train set: {train_accuracy}")
print(f"Accuracy on Test set: {test_accuracy}")


