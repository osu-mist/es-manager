ES Manager
----------

esmanager.py is a script which syncs locations from the [locations-api][]
to an elasticsearch cluster.

[locations-api]: https://github.com/osu-mist/locations-api

### Example

    python3 esmanager.py -i locations -t locations locations.ndjson

This command reads locations from locations.ndjson and uploads theme to the
elasticsearch instance at localhost, using index "locations" and document type
"locations".

If there are any locations on the elasticsearch server that are not present
in the json file, those locations will be deleted; the deleted locations will
be printed to stdout (for posterity), and es-manager will exit with an exit
code of 1.

If running esmanager would cause too many locations to be deleted (currently 5),
then esmanager will refuse to continue unless the --force flag is given. 
This threshold includes locations that have their id changed, since a change of id
appears to esmanager to be an addition and a deletion.
The threshold is governed by the  `SANITY_THRESHOLD` variable in `esmanager.py`.

The format of locations.ndjson is line-separated json objects. See [ndjson.org for more info](http://ndjson.org/)
