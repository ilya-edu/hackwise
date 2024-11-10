# app/jobs/create_slide_job.rb
class CreateSlideJob < ApplicationJob
  queue_as :default

  def perform(article_id)
    article = Article.find(article_id)

    if article.pdf.attached?
      article.pdf.open(tmpdir: Dir.tmpdir) do |file|
        # Send the file to your API
        response = send_file_to_api(file, article.pdf.filename.to_s)
        # Process the API response
        if response.success?
          process_api_response(article, response.parsed_response)
        else
          Rails.logger.error "Error sending PDF for Article #{article_id}: #{response.code} - #{response.body}"
        end
      end
    else
      Rails.logger.error "Article #{article_id} does not have an attached PDF file."
    end
  end

  private

  def send_file_to_api(file_io, file_name)
    require 'httparty'

    options = {
      body: {
        file: file_io
      },
      headers: {
        'Content-Type' => 'multipart/form-data'
      }
    }

    # Send the POST request
    response = HTTParty.post("#{ENV['OCR_URL']}/process-pdf", options)
    response
  end
  def process_api_response(article, response_body)
    slides_data = response_body["slides"]
    slides_data.each do |slide_data|
      slide = article.chunks.create(
        slide_number: slide_data["slide_number"],
        content: slide_data["slide_text"],
        source: 'manual_upload',

      )

      # Attach slide image if available
      image_data = slide_data["image_base64"]
      if image_data.present?
        decoded_image = Base64.decode64(image_data)
        slide.slide.attach(
          io: StringIO.new(decoded_image),
          filename: "slide_#{slide.slide_number}.png",
          content_type: 'image/png'
        )
      end
    end
  end
end
