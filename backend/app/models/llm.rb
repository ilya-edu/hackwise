require 'httparty'

class Llm
  include HTTParty
  default_timeout 5000

  def self.call(system_prompt:, user_prompt:, documents:)
    url = Config.first_or_create.llm_url
    raise 'Set LLM URL' if url.blank?
    puts( {system_prompt: , query: user_prompt, documents: })
    response = post("#{url}/generate", body: {system_prompt: , query: user_prompt, documents: }.to_json, headers: { 'Content-Type' => 'application/json' })
    if response.success?
      {message: response.parsed_response['output'], relevant: response.parsed_response['relevant'], success: true}
    else
      { error: "Failed LLM: #{response.message}" }
    end
  end

end
