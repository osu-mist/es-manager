ES Manager
----------

esmanager.py is a script which syncs locations from the [locations-api][]
to an elasticsearch cluster.

[locations-api]: https://github.com/osu-mist/locations-api

### Example

    python3 esmanager.py -i locations -t locations locations.json

This command reads locations from locations.json and uploads theme to the
elasticsearch instance at localhost, using index "locations" and document type
"locations".

If there are any locations on the elasticsearch server that are not present
in the json file, those locations will be deleted; the deleted locations will
be printed to stdout (for posterity), and es-manager will exit with an exit
code of 1.

If running esmanager would cause the overall size of the database to shrink by
more than some threshold (currently 100), then esmanager will refuse to
continue unless the --force flag is given.

The format of locations.json is line-separated json objects.
