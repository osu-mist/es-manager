import argparse
import io
import json
import logging
import sys

from pprint import pprint

import elasticsearch2
import elasticsearch2.helpers

INDEX = "locations"
TYPE = "locations"

# If the database size would decrease by this number or more,
# require the --force flag
SANITY_THRESHOLD = 100

# input format: resource objects in json format, one per line

def get_current_object_ids(es, index, type):
    """Returns a list of ids

    :param es: an elasticsearch client
    :return: list of object ids
    """

    ids = []
    scan = elasticsearch2.helpers.scan(es,
        index=index,
        doc_type=type,
        _source=False, # don't include bodies
    )

    for obj in scan:
        ids.append(obj['_id'])
    return ids

def read_objects(f):
    """Read a stream of line-delimited json objects from a file-like object."""
    for line in f:
        j = json.loads(line)
        yield j['id'], line.strip()

def main():
    logger = logging.getLogger("esmanager")
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", metavar="locations.json",
        help="locations")
    parser.add_argument("--host", metavar="host[:port]", default='localhost',
        help="elasticsearch server")
    parser.add_argument("-f", "--force", action="store_true", default=False,
        help="proceed even if a large number of locations would be deleted")
    parser.add_argument("-n", "--dry-run", action="store_true", default=False,
        help="build bulk query but don't execute it")
    parser.add_argument("-i", "--index", default=INDEX,
        help="elasticsearch index")
    parser.add_argument("-t", "--type", default=TYPE,
        help="elasticsearch document type")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN starting")

    es = elasticsearch2.Elasticsearch([args.host])

    # Get current list of IDs from ES
    try:
        old_ids = set(get_current_object_ids(es, args.index, args.type))
    except elasticsearch2.exceptions.NotFoundError:
        # index not found, which means there are no old locations to worry about
        old_ids = set()

    # Body for the bulk query
    body = io.StringIO()

    # Remember how many objects were in the database,
    # so we can do a sanity check later.
    number_of_old_objects = len(old_ids)

    with open(args.filename) as f:
        objects = read_objects(f)

        # Keep track of how many objects we'll be adding to the database
        number_of_new_objects = 0

        for id, line in objects:
            number_of_new_objects += 1

            # Add object to bulk query
            body.write(json.dumps({"index": {"_id": id}}))
            body.write("\n")
            body.write(line)
            body.write("\n")

            # Remove id from old_ids
            if id in old_ids:
                old_ids.remove(id)
            else:
                logger.info("new location: %s", id)

    # We're going to delete any remaining IDs
    # But first, fetch each deleted document and log it
    old_ids = sorted(old_ids)
    for id in old_ids:
        # Fetch each to-be-deleted document and log it.
        # Fetching each deleted document is probably slow
        # but there shouldn't be many of them
        body.write(json.dumps({"delete": {"_id": id}}))
        body.write("\n")
        logger.warning("deleting location: %s", id)
        try:
            source = es.get_source(id=id, index=args.index, doc_type=args.type)
        except elasticsearch2.exceptions.NotFoundError:
            logger.warning("document %s to be deleted, but does not exist", id)
        else:
            logger.warning("deleted document: %s", json.dumps(source))

    # Last sanity check:
    # if the database would become much smaller,
    # refuse to continue unless --force was given
    difference = number_of_new_objects - number_of_old_objects
    if difference <= -SANITY_THRESHOLD:
        logger.warning("database would shrink by %d objects", -difference)
        if not args.force:
            logger.error("refusing to continue without the --force flag")
            sys.exit(1)

    print("="*80)

    # do the bulk query
    if args.dry_run:
        print("DRY RUN - not issuing query to elasticsearch")
    else:
        response = es.bulk(body=body.getvalue(), index=args.index, doc_type=args.type)
        pprint(response)

    print("="*80)

    if args.dry_run:
        print("DRY RUN finished")
        print("no data was harmed in the execution of this script :)")

    if old_ids:
        verb = "were deleted" if not args.dry_run else "would be deleted"
        print("some locations {}, exiting with non-zero status".format(verb))
        sys.exit(1)

main()
