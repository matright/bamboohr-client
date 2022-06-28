import argparse
from datetime import date
from dateutil.relativedelta import relativedelta
import os
import requests
import json
import pandas as pd
import plotly.express as px

parser = argparse.ArgumentParser()

parser.add_argument('--date-start', default=str(date.today()))
parser.add_argument('--date-end', default=str(date.today()+relativedelta(months=3)))
parser.add_argument('--request-status', default='approved')
parser.add_argument('--team_name', default='My team')
parser.add_argument('--api_key_env_var', default='BAMBOOHR_KEY')
parser.add_argument('--base_url', default='https://api.bamboohr.com/api/gateway.php/')
parser.add_argument('--tenant', default='bloomreach')
parser.add_argument('--api_version', default='/v1')
parser.add_argument('--endpoint', default='/time_off/requests/')

args = parser.parse_args()

base_url = args.base_url + args.tenant + args.api_version
query_string = "?start="+ args.date_start +"&end="+ args.date_end +"&status="+ args.request_status

# request data to Bamboo API
headers = {"Accept": "application/json"}
response = requests.get(
    base_url+args.endpoint+query_string, headers=headers, 
    auth=(os.getenv(args.api_key_env_var),'xxx')
)

# dump API response into pandas dataframe, consider the last day as a whole, order by name
df = pd.DataFrame(json.loads(response.text))
df = df.assign(end=lambda x: x['end']+' 23:59')
df = df.sort_values("name")

# create timeline chart
fig = px.timeline(df, x_start="start", x_end="end", y="name", title=args.team_name+" holiday overview - from: "+args.date_start+" to: "+args.date_end)
fig.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up

# add today's line to chart
fig.update_layout(shapes=[dict(type='line',yref='paper', y0=0, y1=1,xref='x', x0=date.today(), x1=date.today(), name="Today")])

# show the chart
fig.show()