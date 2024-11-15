class Message < ApplicationRecord
  belongs_to :user
  belongs_to :room
  after_create_commit -> (message) { MessageRelayJob.perform_later(message) }
  validates :text, presence: true
end
