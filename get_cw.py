#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from argparse import ArgumentParser
import time
import os
from datetime import datetime
import os.path

import boto

if __name__ == "__main__":
    # get authentication
    parser = ArgumentParser(description='Generate cloudwatch csv files for ELB.')
    parser.add_argument('--lb', action="append", help="elbs")
    parser.add_argument('--id', help="AWS ID")
    parser.add_argument('--key', help="AWS access key")
    parser.add_argument('--output', help="Output directory", required=True)
    args = parser.parse_args()

    lbs = args.lb

    aws_key = args.key if args.key else os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_id = args.id if args.id else os.getenv("AWS_ACCESS_KEY_ID")
    if aws_id is None:
        parser.error("amazon secret id required")
    if aws_key is None:
        parser.error("amazon secret key required")

    CW = boto.connect_cloudwatch(
        # read only dashboard IAM role
        aws_access_key_id=aws_id,
        aws_secret_access_key=aws_key)

    # |  list_metrics(self, next_token=None, dimensions=None, metric_name=None, namespace=None)
    # |      Returns a list of the valid metrics for which there is recorded
    # |      data available.
    # |
    # |      :type next_token: str
    # |      :param next_token: A maximum of 500 metrics will be returned
    # |          at one time.  If more results are available, the ResultSet
    # |          returned will contain a non-Null next_token attribute.
    # |          Passing that token as a parameter to list_metrics will
    # |          retrieve the next page of metrics.
    # |
    # |      :type dimensions: dict
    # |      :param dimensions: A dictionary containing name/value
    # |          pairs that will be used to filter the results.  The key in
    # |          the dictionary is the name of a Dimension.  The value in
    # |          the dictionary is either a scalar value of that Dimension
    # |          name that you want to filter on or None if you want all
    # |          metrics with that Dimension name.  To be included in the
    # |          result a metric must contain all specified dimensions,
    # |          although the metric may contain additional dimensions beyond
    # |          the requested metrics.  The Dimension names, and values must
    # |          be strings between 1 and 250 characters long. A maximum of
    # |          10 dimensions are allowed.
    # |
    # |      :type metric_name: str
    # |      :param metric_name: The name of the Metric to filter against.  If None,
    # |          all Metric names will be returned.
    # |
    # |      :type namespace: str
    # |      :param namespace: A Metric namespace to filter against (e.g. AWS/EC2).
    # |          If None, Metrics from all namespaces will be returned.
    metrics = CW.list_metrics(namespace="AWS/ELB")

    for aws_m in metrics:
        if "Namespace" in aws_m.dimensions or "Service" in aws_m.dimensions:
            # Duplicated "global" metrics
            continue
        # skip availability zone specific counters
        if "AvailabilityZone" in aws_m.dimensions:
            continue
        # skip counters if no ELB is defined
        if "LoadBalancerName" not in aws_m.dimensions:
            continue

        lb = aws_m.dimensions['LoadBalancerName'][0]
        if lbs and (lb not in lbs):
            continue

        now = time.time()
        start_time = datetime.fromtimestamp(now - 62 * 60)  # 1 hour ago
        end_time = datetime.fromtimestamp(now)

        queried = aws_m.query(
            start_time=start_time,
            end_time=end_time,
            statistics=["Average", "Sum", "SampleCount", "Maximum", "Minimum"],
            period=60)
        if not queried:
            continue
        # sort by time
        queried.sort(key=lambda e: time.mktime(e["Timestamp"].timetuple()))
        series = []
        for q in queried:
            m = {
                "lb": lb,
                "metric": aws_m.name,
                "ts": int(time.mktime(q["Timestamp"].timetuple())),
                "samples": q["SampleCount"],
                "sum": q["Sum"],
                "max": q["Maximum"],
                "min": q["Minimum"],
                "avg": q["Average"],
                "unit": q["Unit"].lower() \
                    .replace("count", "cnt").replace("seconds", "s"),
            }
            series.append(m)
        # print last m
        print("%s" % (now - m["ts"]), end=" ")
        print("%s" % time.ctime(m["ts"]), end=" ")
        print("%(ts)s %(lb)s %(metric)s %(sum)s %(avg)s %(min)s %(max)s %(unit)s" % (m))

        series.reverse()

        output_file = os.path.join(args.output, "%(lb)s-%(metric)s.csv" % m)
        output_file_tmp = "%s.tmp" % output_file

        with open(output_file_tmp, "w") as f:
            for m in series:
                f.write("%(ts)s,%(sum)s,%(min)s,%(max)s,%(avg)s,%(unit)s\n" % m)

        os.rename(output_file_tmp, output_file)
