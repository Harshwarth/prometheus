from flask import Response, Flask
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge
import opsgenie_sdk
import time

# opsgenie api configuration
configuration = opsgenie_sdk.Configuration()
configuration.api_key['Authorization'] = ''
api_client = opsgenie_sdk.api_client.ApiClient(configuration=configuration)
alert_api = opsgenie_sdk.AlertApi(api_client=api_client)

# flask initialization
app = Flask(__name__)

# Prometheus Metrics
metrics = {}
metrics['Total_Alerts'] = Gauge('Total_Alerts', 'Total no. of alerts')
metrics['Total_Open_Alerts'] = Gauge('Total_Open_Alerts', 'Total no. Open of alerts')
# MDM METRICS
metrics['MDM_C'] = Counter('MDM_request_total', 'The total number of processed requests')
metrics['MDM_G_TOTAL'] = Gauge('MDM_Total_Alerts', 'Total no. of MDM alerts')
metrics['MDM_H'] = Histogram('MDM_request_duration_seconds', 'MDM Histogram for the duration in seconds.')
# CAI METRICS
metrics['CAI_C'] = Counter('CAI_request_total', 'The total number of processed requests')
metrics['CAI_G_TOTAL'] = Gauge('CAI_Total_Alerts', 'Total no. of CAI alerts')
metrics['CAI_H'] = Histogram('CAI_request_duration_seconds', 'CAI Histogram for the duration in seconds.')
# APIM METRICS
metrics['APIM_C'] = Counter('APIM_request_total', 'The total number of processed requests')
metrics['APIM_G_TOTAL'] = Gauge('APIM_Total_Alerts', 'Total no. of APIM alerts')
metrics['APIM_H'] = Histogram('APIM_request_duration_seconds', 'APIM Histogram for the duration in seconds.')
# Taskflow
metrics['Taskflow_C'] = Counter('Taskflow_request_total', 'The total number of processed requests')
metrics['Taskflow_G_TOTAL'] = Gauge('Taskflow_Total_Alerts', 'Total no. of Taskflow alerts')
metrics['Taskflow_H'] = Histogram('Taskflow_request_duration_seconds', 'Taskflow Histogram for the duration in seconds.')


def alert_id(product_name):
    ids = []
    list_response = alert_api.list_alerts(sort='createdAt',order='asc')
    for response in list_response.data:
        if product_name in response.tags:
            ids.append(response.id)
    return ids

def products(product_name):
    start = time.time()
    metrics[f'{product_name}_C'].inc()

    count_response_all = alert_api.count_alerts()
    metrics['Total_Alerts'].set(count_response_all.data.count)

    count_response_open = alert_api.count_alerts(query='open')
    metrics['Total_Open_Alerts'].set(count_response_open.data.count)

    alert_ids = alert_id(product_name)
    metrics[f'{product_name}_G_TOTAL'].set(len(alert_ids))

    All_alerts = {}
    c = 1
    for id in alert_ids:
        get_response = alert_api.get_alert(identifier=id, identifier_type='id')
        All_alerts[f"Alert {c}"] = get_response
        c += 1
    end = time.time()
    metrics[f'{product_name}_H'].observe(end - start)
    return All_alerts

# list opsgenie alerts
@app.route("/<product_name>")
def Alerts(product_name):
    if product_name == "MDM" or product_name == "CAI" or product_name == "APIM" or product_name == "Taskflow":
        All_alerts = products(product_name)
        return f"ALERTS <br> {All_alerts}"
    return "<h1>Enter correct product</h1>"

# list metrics
@app.route("/metrics")
def requests_count():
    res = []
    for k, v in metrics.items():
        res.append(prometheus_client.generate_latest(v))
    return Response(res, mimetype="text/plain")

app.run(debug = True)