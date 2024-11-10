class Room < ApplicationRecord
  has_many :messages, dependent: :destroy
  has_many :users, through: :messages
  belongs_to :creator, class_name: 'User', optional: true

  def name
    "Комната пользователя #{creator&.name}"
  end

  after_create_commit -> (room) {RoomRelayJob.perform_later(room)}
end
