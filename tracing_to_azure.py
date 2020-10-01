#!/usr/bin/env python

# Utilities
import os
import time
import logging 
from dotenv import load_dotenv
from random import randint
# Traces
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer
from opencensus.trace.span import SpanKind
from opencensus.trace.status import Status
from opencensus.trace import Span, config_integration
# Logs
from opencensus.ext.azure.log_exporter import AzureLogHandler
# Metrics - not yet sure how this works
from opencensus.ext.azure import metrics_exporter

def main():
    # 4. Create a scoped span. The span will close at the end of the block.
    with tracer.span("main") as span:
        span.span_kind = SpanKind.SERVER

        span.add_annotation("this is an annotaion - entry point to busy work")
        for i in range(randint(1, 10)):
            if i%5 == 0:
                doExtraWork(i)
            doWork()

def doWork():
    # 5. Start another span. Because this is within the scope of the "main" span,
    # this will automatically be a child span.
    with tracer.span(name="doWork") as span:
        msg="doing busy work"
        print(msg)
        # - warning should show as a trace in app insights
        logger.warning(msg)
        try:
            time.sleep(0.1)
        except:
            # 6. Set status upon error
            span.status = Status(5, "Error occurred")

        # 7. Annotate our span to capture metadata about our operation
        span.add_annotation("invoking doWork")

def doExtraWork(counter):
    with tracer.span(name="doExtraWork") as span:
        
        msg="doing other busy work"
        print(msg)
        # - info won't show in app insights
        logger.info(msg)

        try:
            time.sleep(0.1)
            print(1/0)
        except:
            # 6. Set status upon error
            print("Error!")
            logger.error("error should be a trace in app insights")
            logger.exception('Captured an exception')
            span.status = Status(5, "Error occurred")

        # 7. Annotate our span to capture metadata about our operation
        span.add_annotation(f"invoking doWork for:{counter}")

if __name__ == "__main__":
    print("AZURE logging sample...")

    #load env variables for this session
    load_dotenv()
    try:
        # for local testing, set these in the .env file
        APPINSIGHTS_INSTRUMENTATIONKEY = os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"]
    except KeyError:
        print("Please set the environment variable(s): APPINSIGHTS_INSTRUMENTATIONKEY")

    # set up logging 
    config_integration.trace_integrations(['logging'])
    logger = logging.getLogger(__name__)

    handler = AzureLogHandler(connection_string=f'InstrumentationKey={APPINSIGHTS_INSTRUMENTATIONKEY}')
    handler.setFormatter(logging.Formatter('%(traceId)s %(spanId)s %(message)s'))
    logger.addHandler(handler)

    # 1b. Set the tracer to use the exporter
    # 2. Configure 100% sample rate, otherwise, few traces will be sampled.
    # 3. Get the global singleton Tracer object
    tracer = Tracer(exporter=AzureExporter(connection_string=f'InstrumentationKey={APPINSIGHTS_INSTRUMENTATIONKEY}'),sampler=ProbabilitySampler(1.0))

    # ---  Exporter for metrics - (nils: can't see this in app insights - not sure where to find it)
    # All you need is the next line. You can disable performance counters by
    # passing in enable_standard_metrics=False into the constructor of
    # new_metrics_exporter()
    _exporter = metrics_exporter.new_metrics_exporter(connection_string=f'InstrumentationKey={APPINSIGHTS_INSTRUMENTATIONKEY}')

    logger.addHandler(AzureLogHandler(connection_string=f'InstrumentationKey={APPINSIGHTS_INSTRUMENTATIONKEY}'))
    main()
    print("AZURE logging done!")