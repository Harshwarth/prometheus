from flask import Response, Flask
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
import opsgenie_sdk
import time

# opsgenie api configuration
configuration = opsgenie_sdk.Configuration()
configuration.api_key['Authorization'] = '3b5d25f3-8983-48ff-9154-137b6ac0a23d'
api_client = opsgenie_sdk.api_client.ApiClient(configuration=configuration)
alert_api = opsgenie_sdk.AlertApi(api_client=api_client)

# flask initialization
app = Flask(__name__)

# Prometheus Metrics
metrics = {}
metrics['c'] = Counter('python_request_operations_total', 'The total number of processed requests')
metrics['g_total'] = Gauge('Total_Alerts', 'Total no. of alerts in ops genie')
metrics['g_open'] = Gauge('Open_Alerts', 'Total no. of open alerts in ops genie')
metrics['h'] = Histogram('python_request_duration_seconds', 'Histogram for the duration in seconds.')

# list opsgenie alerts
@app.route("/")
def Alerts():
    start = time.time()
    metrics['c'].inc()
    list_response_all = alert_api.list_alerts()
    list_response_open = alert_api.list_alerts(query='open')
    count_response_all = alert_api.count_alerts()
    metrics['g_total'].set(count_response_all.data.count)
    count_response_open = alert_api.count_alerts(query='open')
    metrics['g_open'].set(count_response_open.data.count)
    end = time.time()
    metrics['h'].observe(end - start)
    return f"ALL ALERTS: <br> {list_response_all.data} <br><br> OPEN ALERTS:<br> {list_response_open.data}"

# list metrics
@app.route("/metrics")
def requests_count():
    res = []
    for k, v in metrics.items():
        res.append(prometheus_client.generate_latest(v))
    return Response(res, mimetype="text/plain")

app.run(debug = True)