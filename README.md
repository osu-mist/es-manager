ES Manager
----------

es-manager.py is a script which syncs locations from the [locations-api][]
to an elasticsearch cluster.

[locations-api]: https://github.com/osu-mist/locations-api

### Example

    python3 es-manager.py -i locations -t locations locations.json

This command reads locations from locations.json and uploads theme to the
elasticsearch instance at localhost, using index "locations" and document type
"locations".

If there are any locations on the elasticsearch server that are not present
in the json file, those locations will be deleted; the deleted locations will
be printed to stdout (for posterity), and es-manager will exit with an exit
code of 1.

The format of locations.json is line-separated json objects.
