import pymongo
import pprint
import json
import urllib
"""

Methods for managing views:

createView(idb, view_name, view_definition) - creates a view in the idb database
getView(idb,view_name) - gets the json representation of the view from the DB
drop(view(idb,view_name) - drops the view (has to be a view)

"""


def createView(idb, view_name, view_definition):
    viewOn = view_definition["view_on"]
    pipeline = view_definition["pipeline"]
    idb.command('create', view_name, viewOn=viewOn, pipeline=pipeline)


def getView(idb, view_name):
    return idb.command('listCollections',
                       filter={
                           'name': view_name,
                           'type': 'view'
                       })


def dropView(idb, view_name):
    test = getView(idb, view_name)
    if len(test['cursor']['firstBatch']) == 0:
        raise Exception("No View of name " + view_name)
    view = idb[view_name]
    view.drop()


def test(db):

    viewName = "testview_do_not_use"
    viewon_table = "science_view"
    viewjson_text = """{
      "view_on":viewon_table,
      "pipeline":[{"$project": {"challenge_problem": "$challenge_problem",
        "experiment_reference_url": "$experiment.experiment_reference_url",
        "experiment_reference": "$experiment.experiment_reference",
        "experiment_id": "$experiment.experiment_id",
        "filename": "$file.filename",
        "temperature": "$sample.temperature",
        "strain": "$sample.strain.label",
        "level": "$file.level",
        "strain_sbh_uri": "$sample.strain.sbh_uri",
        "inoculation_density": "$sample.inoculation_density",
        "replicate": "$sample.replicate",
        "strain_lab_id": "$sample.strain.lab_id",
        "strain_input_state": "$sample.strain.input_state",
        "strain_circuit": "$sample.strain.circuit",
        "lab": "$sample.attributes.lab",
        "sample_contents": "$sample.contents",
        "measurement_type": "$measurement.measurement_type",
        "file_type": "$file.attributes.file_type",
        "aligner": "$file.attributes.aligner",
        "agave_system": "$agave_path.agave_system",
        "agave_path": {"$concat": ["$agave_path.path_prefix",
          "/",
          "$file.filename"]},
        "jupyter_path": {"$concat": ["/home/jupyter/sd2e-community",
          "$agave_path.path_prefix",
          "/",
          "$file.filename"]},
        "hpc_path": {"$concat": ["/work/projects/SD2E-Community/prod/data",
          "$agave_path.path_prefix",
          "/",
          "$file.filename"]},
        "reference_sample_id": "$sample.reference_sample_id",
        "sample_id": "$sample.sample_id",
        "timepoint": "$measurement.timepoint",
        "normalization": "$file.attributes.normalization",
        "library_prep": "$file.attributes.library_prep"}}]"""

    pprint.pprint(getView(db, viewName))

    createView(db, viewName, json.loads(viewjson_text))

    pprint.pprint(getView(db, viewName))

    dropView(db, viewName)

    pprint.pprint(getView(db, viewName))
