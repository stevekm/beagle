import uuid
from rest_framework import serializers
from runner.operator.operator import Operator
from runner.serializers import APIRunCreateSerializer
from .construct_tempo_pair import construct_tempo_jobs
from .bin.pair_request import compile_pairs
from .bin.make_sample import build_sample


class TempoOperator(Operator):
    def get_jobs(self):
        files = self.files.filter(filemetadata__metadata__requestId=self.request_id, filemetadata__metadata__igocomplete=True).all()
        tempo_jobs = list()

        data = list()
        for file in files:
            sample = dict()
            sample['id'] = file.id
            sample['path'] = file.path
            sample['file_name'] = file.file_name
            sample['metadata'] = file.filemetadata_set.first().metadata
            data.append(sample)

        samples = list()
        # group by igoId
        igo_id_group = dict()
        for sample in data:
            igo_id = sample['metadata']['sampleId']
            if igo_id not in igo_id_group:
                igo_id_group[igo_id] = list()
            igo_id_group[igo_id].append(sample)

        for igo_id in igo_id_group:
            samples.append(build_sample(igo_id_group[igo_id]))

        tempo_inputs, error_samples = construct_tempo_jobs(samples)
        number_of_inputs = len(tempo_inputs)

        for i, job in enumerate(tempo_inputs):
            name = "FLATBUSH: %s, %i of %i" % (self.request_id, i + 1, number_of_inputs)
            tempo_jobs.append((APIRunCreateSerializer(
                data={'app': self.get_pipeline_id(), 'inputs': tempo_inputs, 'name': name,
                      'tags': {'requestId': self.request_id}}), job))

        return tempo_jobs
