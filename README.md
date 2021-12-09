# IATI Data Store Classic - Matomo Import

This is used on: https://datastore.codeforiati.org/

This is a python Script that parses Apache logs then sends each hit to Matomo's API.

It only parses API access - things that start with `/api`.
(Everything else is tracked with usual javascript means)

It attempts to weed out "bots" by having a list of bot User Agents strings.

For each access it wants to log, it puts data in custom dimensions.
The ID's of these custom dimensions are hardcoded in `CUSTOM_DIMENSION_*` variables.

The apache log format should be specified in the `APACHE_LOG_FILE_FORMAT` variable.

Matomo does not de-dupe the entries in any way, so each entry must only be sent once.
This is achieved by a daily cron job that sends yesterday's log file.

On our servers, this script is setup by salt. See: https://github.com/OpenDataServices/opendataservices-deploy/blob/main/salt/iatidatastoreclassic.sls

Pass parameters:
  * `file` - path + name of the log file to parse
  * `host` - Matomo host to send to. eg `https://matomo.YOURDOMAIN.com/`
  * `token` - Matomo's API token
  * `siteid` - integer - site id to log to

