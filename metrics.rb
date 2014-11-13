require "fog"

class Metrics

  attr_reader :elb_name

  def initialize(elb_name)
    @elb_name = elb_name
  end

  def request_count
    format statistics("RequestCount")
  end

  def http_code_backend_5xx
    format statistics("HTTPCode_Backend_5XX")
  end

  def latency
    format statistics("Latency")
  end

  def statistics(metric_name)
    conditions = {
                  "Namespace" => "AWS/ELB",
                  "Dimensions" => [{"Name" => "LoadBalancerName", "Value" => elb_name}],
                  "StartTime" => (Time.now-60*60).iso8601,
                  "EndTime" => Time.now.iso8601,
                  "Period" => 60,
                  "MetricName" => metric_name,
                  "Statistics" => %w[Sum Minimum Maximum Average SampleCount]
                 }
    cloud_watch_api.get_metric_statistics(conditions).body['GetMetricStatisticsResult']['Datapoints']
  end

  def format(data)
    data.sort_by{ |d| d["Timestamp"] }.inject("") do |m, e| 
      unit = e['Unit'].downcase.sub("count", "cnt").sub("seconds", "s")
      sum = "%f" % e['Sum']
      minimum = "%f" % e['Minimum']
      maximum = "%f" % e['Maximum']
      average = "%f" % e['Average']
      m << "#{e['Timestamp'].to_i},#{sum},#{minimum},#{maximum},#{average},#{unit}\n"
      m
    end
  end

  def aws_access_key_id
    @aws_access_key_id ||= ENV["AWS_ACCESS_KEY_ID"]
  end

  def aws_secret_access_key
    @aws_secret_access_key ||= ENV["AWS_SECRET_ACCESS_KEY"]
  end

  def common_aws_options
    {
     :aws_access_key_id => aws_access_key_id,
     :aws_secret_access_key => aws_secret_access_key,
    }
  end

  def cloud_watch_endpoint
    @cloud_watch_endpoint ||= endpoint_parse(ENV["AWS_CLOUD_WATCH_ENDPOINT"] || "https://monitoring.#{region}.amazonaws.com:443/")
  end

  def region
    @region ||= ENV["PROVIDER_REGION"] || "us-east-1"
  end

  def endpoint_parse(aws_endpoint)
    endpoint = URI.parse(aws_endpoint)
    # Empty paths produce SSL errors due to AWS API signing.
    if endpoint.path == ""
      endpoint.path = "/"
    end
    return {
            :host => endpoint.host,
            :path => endpoint.path,
            :port => endpoint.port,
            :scheme => endpoint.scheme }
  end

  def cloud_watch_api
    @cloud_watch_api ||= Fog::AWS::CloudWatch.new(common_aws_options.merge(cloud_watch_endpoint).merge(:region => region))
  end
end
