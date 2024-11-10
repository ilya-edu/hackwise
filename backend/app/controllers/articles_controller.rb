class ArticlesController < ApplicationController


  def new;end
  def create
    file = params[:file_upload]
    ParseSlidesJob.perform_later(file.read.delete("\0"))
  end

  def upload_batch_search
    @submits = Submit.all.order(created_at: :desc)
  end

  def index
    @chunks = SemanticSearch.new.perform(query, :chunks, article_id: params[:article_id])
  end

  def query
    params[:query] || ' '
  end

end
