class ParseSlidesJob < ApplicationJob
  queue_as :parsers
  def perform(file)
    csv = CSV.parse(file)
    headers = csv.shift
    csv.each do |line|
      content = line[headers.index('slide_text')]
      title = line[headers.index('file_name')]
      slide_number = line[headers.index('slide_number')]
      source = line[headers.index('source')]
      article = Article.find_or_create_by(link: title, name: title )
      Chunk.create(article:, slide_number:, content: content.gsub(/\s+/, ' '), source:   ) if content.present?
    end
  end
end