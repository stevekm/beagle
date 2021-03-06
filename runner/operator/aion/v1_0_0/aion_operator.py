"""
Aion Operator

Constructs input JSON for the Aion pipeline and then
submits them as runs
"""
import os
import datetime
import logging
from notifier.models import JobGroup
from runner.models import Run
from runner.operator.operator import Operator
from runner.serializers import APIRunCreateSerializer
from runner.models import Pipeline
LOGGER = logging.getLogger(__name__)


class AionOperator(Operator):
    def get_jobs(self, lab_head_email):
        """
        From self, retrieve relevant run IDs, build the input JSON for
        the pipeline, and then submit them as jobs through the
        APIRunCreateSerializer
        """
        run_ids = self.get_helix_filter_run_ids(lab_head_email)
        number_of_runs = len(run_ids)
        name = "AION merging %i runs for lab head email %s" % (
            number_of_runs, lab_head_email)

        app = self.get_pipeline_id()
        pipeline = Pipeline.objects.get(id=app)
        pipeline_version = pipeline.version
        input_json = self.build_input_json(run_ids)
        tags = { "study_id": input_json['study_id'], "num_runs_merged": len(run_ids)}
        print(input_json)

        aion_outputs_job_data = {
            'app': app,
            'inputs': input_json,
            'name': name,
            'tags': tags}

        aion_outputs_job = [(APIRunCreateSerializer(
            data=aion_outputs_job_data), input_json)]

        return aion_outputs_job
    
    
    def build_input_json(self, run_ids):
    #    run_ids = self.run_ids
        project_prefixes = set()
        directories = set()
        lab_heads = set()
        argos_run_ids = set()
    
        for run_id in run_ids:
            run = Run.objects.get(id=run_id)
            argos_run_ids = run.tags['run_ids']
            project_prefix = run.tags['project_prefix']
            if project_prefix:
                project_prefixes.add(project_prefix)
            run_portal_dir = os.path.join(run.output_directory, "portal")
            if os.path.isdir(run_portal_dir):
                directories.add(run_portal_dir)
        merge_date = datetime.datetime.now().strftime("%Y_%m_%d")
        lab_head_email = self.get_lab_head(argos_run_ids)
        input_json = dict()
        lab_head_id = lab_head_email.split("@")[0]
        study_id = "set_%s" % lab_head_id 
        input_json["project_description"] = "[%s] Includes samples received at IGO for Project ID(s): %s" % (merge_date, ", ".join(sorted(project_prefixes)))
        input_json["study_id"] = study_id
        input_json["project_title"] = "CMO Merged Study for Principal Investigator (%s)" % study_id
        input_json["directories"] = list()
        for portal_directory in directories:
            input_json["directories"].append({"class": "Directory", "path": portal_directory})
        return input_json
    
    
    def get_lab_head(self, argos_run_ids):
        lab_head_emails = set()
        for argos_run_id in argos_run_ids:
            argos_run = Run.objects.get(id=argos_run_id)
            lab_head_email = argos_run.tags['labHeadEmail']
            if lab_head_email:
                lab_head_emails.add(lab_head_email)
        if len(lab_head_emails) > 1:
    #         LOGGER.warn("Multiple lab head emails found; merge output directory unclear.")
            print("Multiple lab head emails found; merge output directory unclear.")
        # TODO: get clarity on where to output if there are multiple pi found
        if lab_head_emails:
             return sorted(lab_head_emails)[0]
        return None
    
    
    def get_helix_filter_run_ids(self, lab_head_email):
        runs = Run.objects.filter(status=4, app__name="argos_helix_filters")
        helix_filter_runs = set()
        for i in runs:
            argos_run_ids = i.tags['run_ids']
            for run_id in argos_run_ids:
                run = Run.objects.get(id=run_id)
                try:
                    curr_lab_head_email = run.tags['labHeadEmail']
                    if lab_head_email.lower() in curr_lab_head_email.lower():
                        helix_filter_runs.add(i.id)
                except KeyError:
                    print("labHeadEmail not in this run %s", run_id)
        return sorted(helix_filter_runs)
