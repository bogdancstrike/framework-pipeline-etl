import json
import os

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.trace import Status, StatusCode
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(dotenv_path=path.join(basedir, '.env'))

# Configure the tracer provider
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: environ.get('JAEGER_SERVICE_NAME')})
    )
)

# Set up the Jaeger exporter and span processor
jaeger_exporter = JaegerExporter(
    agent_host_name=environ.get('JAEGAR_AGENT_HOST_NAME'),
    agent_port=int(environ.get('JAEGER_AGENT_PORT'))
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)
tracer = trace.get_tracer(__name__)


# Function to get the tracer
def get_tracer():
    return tracer
