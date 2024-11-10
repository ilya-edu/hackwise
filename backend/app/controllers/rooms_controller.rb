class RoomsController < ApplicationController
  def index
    @rooms = current_user.admin? ? Room.includes(:messages) : Room.includes(:messages).where(messages: {user: current_user} )
  end
  def destroy
    Room.find(params[:id]).destroy
    head :no_content
  end
end