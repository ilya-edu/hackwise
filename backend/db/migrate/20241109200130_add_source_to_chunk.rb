class AddSourceToChunk < ActiveRecord::Migration[7.1]
  def change
    add_column :chunks, :source, :string
  end
end
