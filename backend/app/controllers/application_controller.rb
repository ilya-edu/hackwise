class ApplicationController < ActionController::Base
  before_action :dummy_auth
  protect_from_forgery with: :null_session
  def dummy_auth
    @current_user = User.find_or_create_by(name: params[:username])
  end
  attr_reader :current_user
  before_action :set_active_storage_url_options

  private

  def set_active_storage_url_options
    ActiveStorage::Current.url_options = { protocol: 'https', host: 'media-wise-api.kovalev.team', port: 443 }
  end
end
