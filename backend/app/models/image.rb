class Image < ApplicationRecord
  include EmbeddingExtractor
  belongs_to :article
  has_one_attached :image
end