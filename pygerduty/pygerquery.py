#!/usr/bin/env python

import __init__ as pygerduty

class PygerdutyQuery:
  """ __init__
  parameters:
    url: your company's pagerduty url
    apikey: the apikey for one of your accounts
  """
  def __init__(self, url, apikey):
    self.pager = pygerduty.PagerDuty(url, apikey)

  """ GetIncidentsSince
  parameters:
    starttime: Starting time using datetime
    offset: skip over the first X incidents
  """
  def GetIncidentsSince(self, starttime, offset=0):
    limit = 100
    params = {'since' : starttime, 'limit' : limit, 'offset' : offset}
    allincidents = []
    incidentbatch = self.pager.request('GET', '/api/v1/incidents', query_params=params)
    allincidents += incidentbatch['incidents']
    if (incidentbatch['total'] - offset) > limit:
      newoffset = offset + limit
      allincidents += self.GetIncidentsSince(starttime, newoffset)

    return allincidents

  def GetIncidentLog(self, incident_id):
    params = { 'is_overview' : 'true' }
    incidentinfo = self.pager.request('GET',
      '/api/v1/incidents/%s/log_entries' % incident_id, query_params=params)
    return incidentinfo

if __name__ == '__main__':
  # example of usage where you want to get the last 7 days of incidents
  import datetime
  starttime = datetime.datetime.now() - datetime.timedelta(days=7)
  p = pygerquery.PygerdutyQuery('your_url.pagerduty.com', 'your_api_key_should_be_here')
  incidents = p.GetIncidentsSince(starttime)
  print incidents
