from os import environ
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import config

# Configure the tracer provider
trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: config.Config.WORKER_NAME})
    )
)

otlp_exporter = OTLPSpanExporter(
    endpoint=f"http://{config.Config.JAEGAR_AGENT_HOST_NAME}:{config.Config.JAEGER_AGENT_PORT}",
    # For insecure connection, useful for testing
    insecure=True
)

trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))
tracer = trace.get_tracer(__name__)


def get_tracer():
    return tracer
