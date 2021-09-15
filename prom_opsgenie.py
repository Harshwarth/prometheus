from flask import Response, Flask
import prometheus_client
from prometheus_client import Counter, Histogram
import opsgenie_sdk
import time

# opsgenie api configuration
configuration = opsgenie_sdk.Configuration()
configuration.api_key['Authorization'] = ''
api_client = opsgenie_sdk.api_client.ApiClient(configuration=configuration)
alert_api = opsgenie_sdk.AlertApi(api_client=api_client)

# flask initialization
app = Flask(__name__)

metrics = {}
metrics['c'] = Counter('python_request_operations_total', 'The total number of processed requests')
metrics['h'] = Histogram('python_request_duration_seconds', 'Histogram for the duration in seconds.')

# list opsgenie alerts
@app.route("/")
def hello():
    start = time.time()
    metrics['c'].inc()
    list_response = alert_api.list_alerts()
    time.sleep(0.600)
    end = time.time()
    metrics['h'].observe(end - start)
    return f"{list_response}"

# list metrics
@app.route("/metrics")
def requests_count():
    res = []
    for k, v in metrics.items():
        res.append(prometheus_client.generate_latest(v))
    return Response(res, mimetype="text/plain")

app.run(debug=True)