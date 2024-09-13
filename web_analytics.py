import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'static\service_account.json'

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)


"""Runs a simple report on a Google Analytics 4 property."""
# TODO(developer): Uncomment this variable and replace with your
#  Google Analytics 4 property ID before running the sample.
property_id = "457343596"

# Using a default constructor instructs the client to use the credentials
# specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
client = BetaAnalyticsDataClient()

request = RunReportRequest(
    property=f"properties/{property_id}",
    dimensions=[Dimension(name="city")],
    metrics=[Metric(name="activeUsers")],
    date_ranges=[DateRange(start_date="2020-03-31", end_date="today")],
)
response = client.run_report(request)

print("Report result:")
for row in response.rows:
    print(row.dimension_values[0].value, row.metric_values[0].value)
