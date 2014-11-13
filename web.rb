require "sinatra"
require "metrics"

class Web < Sinatra::Base
  get "/:name/RequestCount.csv" do
    Metrics.new(params[:name]).request_count
  end

  get "/:name/Latency.csv" do
    Metrics.new(params[:name]).latency
  end

  get "/:name/HTTPCode_Backend_5XX.csv" do
    Metrics.new(params[:name]).http_code_backend_5xx
  end

  get "/" do
    erb :index
  end
end
