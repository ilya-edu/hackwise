class AddSlideNumberToChunk < ActiveRecord::Migration[7.1]
  def change
    add_column :chunks, :slide_number, :integer
  end
end
