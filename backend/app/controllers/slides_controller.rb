class SlidesController < ApplicationController


  def new;end

  def show
    @article = Article.find(params[:id])
  end
  def create
    file = params[:file_upload]

    # Create a new Article instance
    @article = Article.new

    # Assign the file name to 'link' and 'name' attributes
    @article.name = file.original_filename
    @article.link = file.original_filename

    # Attach the uploaded PDF file to the article
    @article.pdf.attach(file)

    if @article.save
      # Optionally, start a background job to process the PDF
      CreateSlideJob.perform_later(@article.id)

      redirect_to slide_path(@article), notice: 'Статья успешно загружена. Пожалуйста, подождите, пока PDF файл обрабатывается. 15 слайдов будут грузится в течение ~20 минут.'
    else
      render :new
    end
  end

end
