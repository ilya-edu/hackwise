class LlmJob < ApplicationJob
  queue_with_priority 2
  queue_as :llm_processing
  def perform(message)
    ActiveStorage::Current.url_options = { protocol: 'https', host: 'media-wise-api.kovalev.team', port: 443 }
    chunks = SemanticSearch.new.perform(message.text, :chunks)[0..2]
    context = build_context(chunks)

    message.update(context: context )
    config = Config.first_or_create
    system_prompt = config.system
    user_prompt = config.user % { query: message.text }
    relevant = []
    text = if config.llm_enabled
             llm_response = Llm.call(system_prompt: , user_prompt:, documents: context )
             if llm_response[:success]
               relevant = llm_response[:relevant]
                      llm_response[:message]
                    else
                      build_fallback_response(chunks)
                    end
           else
             build_fallback_response(chunks)
           end


    Message.create(text: , room_id: message.room_id, user: User.find_or_create_by(name: "admin"), references: build_references(chunks.select{  |chunk| relevant.map(&:to_i).include?(chunk.id)}), context: "#{system_prompt} \n\n\n\n #{user_prompt}"  )
  end
  def build_context(chunks)

    chunks.map do |chunk|
      puts chunk.attributes
      {
        "doc_id": chunk.id,
        "title": "Презентация: #{chunk.article.name} Слайд: #{chunk.slide_number}",
        "content": chunk.search_index
      }
    end
  end

  def build_references(chunks)
    chunks.map do |chunk|
      chunk = Chunk.find(chunk.id)
      {
        name: "Презентация #{chunk.article.name}",
        url: chunk.article.pdf.present? ? "https://media-wise-api.kovalev.team/#{Rails.application.routes.url_helpers.rails_blob_path(chunk.article.pdf, only_path: true)}" : nil ,
        slide_name: "Слайд #{chunk.slide_number}",
        slide_url: chunk.slide.url.present? ? "https://media-wise-api.kovalev.team/#{Rails.application.routes.url_helpers.rails_blob_path(chunk.slide, only_path: true)}" : nil
      }.to_json
    end
  end
  def build_fallback_response(chunks)
    chunks[0..5].map do |chunk|
      article = chunk.article
      next if article.nil?
      <<-TEXT.strip_heredoc
        1. [#{article.summary}](#{article.link})
      TEXT
    end.compact.join("\n\n")
  end
end