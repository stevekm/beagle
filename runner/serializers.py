import datetime
from django.conf import settings
from rest_framework import serializers
from runner.models import Pipeline, Run, Port, RunStatus, PortType, ExecutionEvents


class PipelineResolvedSerializer(serializers.Serializer):
    app = serializers.JSONField()


class PipelineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pipeline
        fields = ('id', 'name', 'github', 'version', 'entrypoint')


class PortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Port
        fields = ('id', 'name', 'schema', 'secondary_files', 'value', 'db_value')


class UpdatePortSerializer(serializers.Serializer):
    values = serializers.ListField()


class CreatePortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Port
        fields = ('run', 'name', 'port_type', 'schema', 'secondary_files', 'value')


class CreateRunSerializer(serializers.Serializer):
    pipeline_id = serializers.UUIDField()

    def create(self, validated_data):
        try:
            pipeline = Pipeline.objects.get(pk=validated_data.get('pipeline_id'))
        except Pipeline.DoesNotExist:
            raise serializers.ValidationError("Unknown pipeline: %s" % validated_data.get('pipeline_id'))
        name = "Run %s: %s" % (pipeline.name, datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        run = Run(name=name, app=pipeline, status=RunStatus.CREATING, job_statuses=dict())
        run.save()
        return run


class UpdateRunSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=False)
    job_statuses = serializers.JSONField(allow_null=True, required=False)

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.job_statuses = validated_data.get('status', instance.job_statuses)
        instance.save()
        return instance


class RunSerializer(serializers.ModelSerializer):
    inputs = serializers.SerializerMethodField()
    outputs = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    status_url = serializers.SerializerMethodField()

    def get_status(self, obj):
        return RunStatus(obj.status).name

    def get_inputs(self, obj):
        return PortSerializer(obj.port_set.filter(port_type=PortType.INPUT).all(), many=True).data

    def get_outputs(self, obj):
        return PortSerializer(obj.port_set.filter(port_type=PortType.OUTPUT).all(), many=True).data

    def get_status_url(self, obj):
        return settings.BEAGLE_URL + '/v0/run/api/%s' % obj.id

    class Meta:
        model = Run
        fields = ('id', 'name', 'status', 'app', 'inputs', 'outputs', 'status_url', 'created_date', 'job_statuses')


class RunStatusUpdateSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=False)
    jobStatus = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
    errFilePath = serializers.CharField(required=False)
    outputs = serializers.JSONField(required=False, allow_null=True)
    processed = serializers.BooleanField(required=False)

    def create(self, validated_data):
        event = ExecutionEvents()
        event.execution_id = validated_data.get('id', None)
        event.name = validated_data.get('name', None)
        event.job_status = validated_data.get('jobStatus', None)
        event.message = validated_data.get('message', None)
        event.err_file_path = validated_data.get('errFilePath', None)
        event.outputs = validated_data.get('outputs', None)
        event.processed = False
        event.save()

    def update(self, instance, validated_data):
        instance.processed = validated_data.get('processed')
        instance.save()


class APIRunCreateSerializer(serializers.Serializer):
    app = serializers.UUIDField()
    inputs = serializers.JSONField(allow_null=True, required=True)
    outputs = serializers.JSONField(allow_null=True, required=False)
    output_directory = serializers.CharField(max_length=1000, required=False, default=None)

    def create(self, validated_data):
        try:
            pipeline = Pipeline.objects.get(id=validated_data.get('app'))
        except Pipeline.DoesNotExist:
            raise serializers.ValidationError("Unknown pipeline: %s" % validated_data.get('pipeline_id'))
        name = "Run %s: %s" % (pipeline.name, datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        run = Run(name=name, app=pipeline, status=RunStatus.CREATING, job_statuses=dict())
        run.save()
        return run


class RequestIdOperatorSerializer(serializers.Serializer):
    request_ids = serializers.ListField(
        child=serializers.CharField(max_length=30)
    )
    pipeline_name = serializers.CharField(max_length=100)
