class SubmissionsController < ApplicationController

  def index
    @submissions = Submit.all.order(created_at: :desc)
  end
  def show
    submit = Submit.find(params[:id])
    send_data submit.file_content,
              type: 'text/csv; charset=utf-8; header=present',
              disposition: "attachment; filename=Submit report #{submit.created_at}.csv"
  end

  def create
    file = params[:file_upload]
    CreateSubmissionJob.perform_now(file)
    redirect_to submissions_url
  end

end

