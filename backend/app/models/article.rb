class Article < ApplicationRecord
  #include EmbeddingExtractor
  belongs_to :version_group, class_name: 'VersionGroup', optional: true
  has_many :images
  has_many :chunks, dependent: :destroy
  has_one_attached :pdf
  def content_for_similarity
    [name, content, version.present? ? "Версия: #{version}" : nil ].compact.join(" ")
  end
end