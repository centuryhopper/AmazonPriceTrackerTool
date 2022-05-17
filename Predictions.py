import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt


#region test code
df = pd.read_csv('./CSVFiles/qnap_network_drive.csv')
df['Year'] = df['Date'].apply(lambda x: str(x).split('-')[0])
df['Month'] = df['Date'].apply(lambda x: str(x).split('-')[1])
df['Day'] = df['Date'].apply(lambda x: str(x).split('-')[2])
df['ds'] = pd.DatetimeIndex(df['Year']+'-'+df['Month']+'-'+df['Day'])
df.drop(['Date', 'Description', 'Year', 'Month', 'Day','Rating', 'Review Count','URL',], axis=1, inplace=True)
df.columns = ['y', 'ds']
df.y = df.y.str[1:]
# print(df)

m = Prophet(interval_width=0.95,daily_seasonality=True)
model = m.fit(df)
# forecast 365 days into the future
future = m.make_future_dataframe(periods=365, freq='D')
forecast_df = m.predict(future)
print(forecast_df.head(10))
print(forecast_df.tail(10))
fig1 = m.plot(forecast_df)
fig2 = m.plot_components(forecast_df)
plt.show()

#endregion