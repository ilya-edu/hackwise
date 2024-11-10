class Chunk < ApplicationRecord
  include EmbeddingExtractor
  belongs_to :article
  has_one_attached :slide

  def content_for_similarity
    [content].compact.join(" ")
  end
end
