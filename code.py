import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Load the data
bikesData = pd.read_csv('hour.csv')

# Create dayCount column
bikesData['dayCount'] = pd.Series(range(bikesData.shape[0]))/24

# Split data into training and test sets
train_set, test_set = train_test_split(bikesData, test_size=0.3, random_state=42)

# Define columns to scale
columnsToScale = ['temp', 'hum', 'windspeed']

# Scale the features
scaler = StandardScaler()
train_set[columnsToScale] = scaler.fit_transform(train_set[columnsToScale])
test_set[columnsToScale] = scaler.transform(test_set[columnsToScale])

# Define training columns and target column
trainingCols = train_set.drop(['cnt', 'casual', 'registered', 'dteday', 'atemp', 'instant'], axis=1)
trainingLabels = train_set['cnt']

# Train the Decision Tree Regressor
dec_reg = DecisionTreeRegressor(random_state=42)
dt_mae_scores = -cross_val_score(dec_reg, trainingCols, trainingLabels, cv=10, scoring='neg_mean_absolute_error')
dt_mse_scores = np.sqrt(-cross_val_score(dec_reg, trainingCols, trainingLabels, cv=10, scoring='neg_mean_squared_error'))

# Train the Linear Regression Model
lin_reg = LinearRegression()
lr_mae_scores = -cross_val_score(lin_reg, trainingCols, trainingLabels, cv=10, scoring='neg_mean_absolute_error')
lr_mse_scores = np.sqrt(-cross_val_score(lin_reg, trainingCols, trainingLabels, cv=10, scoring='neg_mean_squared_error'))

# Train the Random Forest Model
forest_reg = RandomForestRegressor(random_state=42)
rf_mae_scores = -cross_val_score(forest_reg, trainingCols, trainingLabels, cv=10, scoring='neg_mean_absolute_error')
rf_mse_scores = np.sqrt(-cross_val_score(forest_reg, trainingCols, trainingLabels, cv=10, scoring='neg_mean_squared_error'))

# Choose the best model based on RMSE
best_model = forest_reg  # Random Forest Regressor performed the best

# Define hyperparameter grid for GridSearchCV
param_grid = [
    {'n_estimators': [120, 150], 'max_features': [10, 12], 'max_depth': [15, 28]},
]

# Perform GridSearchCV
grid_search = GridSearchCV(best_model, param_grid, cv=5, scoring='neg_mean_squared_error')
grid_search.fit(trainingCols, trainingLabels)

# Get the best estimator and best parameters
final_model = grid_search.best_estimator_
best_params = grid_search.best_params_

# Prepare test set
test_set.sort_values('dayCount', axis=0, inplace=True)
test_x_cols = test_set.drop(['cnt', 'casual', 'registered', 'dteday', 'atemp', 'instant'], axis=1).columns.values
X_test = test_set.loc[:, test_x_cols]
y_test = test_set['cnt']

# Make predictions on the test set
test_set['predictedCounts_test'] = final_model.predict(X_test)

# Calculate RMSE
mse = mean_squared_error(y_test, test_set['predictedCounts_test'])
final_rmse = np.sqrt(mse)
print(f"Final RMSE: {final_rmse}")

# Plot predicted vs. actual values
times = [9, 18]
for time in times:
    fig = plt.figure(figsize=(8, 6))
    fig.clf()
    ax = fig.gca()
    test_set_freg_time = test_set[test_set.hr == time]
    test_set_freg_time.plot(kind='line', x='dayCount', y='cnt', ax=ax)
    test_set_freg_time.plot(kind='line', x='dayCount', y='predictedCounts_test', ax=ax)
    plt.show()