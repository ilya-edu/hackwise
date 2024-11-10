class CreateSubmissionJob < ApplicationJob
  def perform(file)
    csv = CSV.read(file)
    headers = csv.shift # answer_class,Answer,Question,Category
    headers.concat ['question', 'filename', 'slide_number', 'answer']
    csv.map do |line|
      article_id = Article.find_by_name(line[1]).id
      chunks = SemanticSearch.new.perform(line[0], :chunks, article_id: )


      chunk = chunks[0]
      line << chunk.article.name
      line << chunk.slide_number
      line
    end
    csv_string = generate_csv(headers, csv)
    @submit = Submit.create(file_content: csv_string )
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
  def generate_csv(headers, rows)
    CSV.generate do |csv|
      csv << %w[question filename slide_number] # Add headers at the top of the CSV
      rows.each { |row| csv << row }  # Append each row's fields to the CSV
    end
  end
end