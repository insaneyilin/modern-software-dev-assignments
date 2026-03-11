# app/controllers/notes_controller.rb
class NotesController < ApplicationController
  include ActionView::RecordIdentifier

  before_action :set_note, only: [:show, :update, :destroy]

  def index
    @notes = Note.recent
    @note = @notes.first || Note.new
    @query = params[:q]
  end

  def show
    @notes = Note.recent
    @note = Note.find(params[:id])
    @query = params[:q]
    render :index
  end

  def create
    @note = Note.new(title: "Untitled", content: "")

    if @note.save
      redirect_to note_path(@note)
    else
      @notes = Note.recent
      @note = @notes.first || Note.new
      flash[:error] = "创建笔记失败: #{@note.errors.full_messages.join(', ')}"
      render :index, status: :unprocessable_entity
    end
  end

  def update
    if @note.update(note_params)
      respond_to do |format|
        format.html { redirect_to @note }
        format.turbo_stream do
          render turbo_stream: [
            turbo_stream.replace(dom_id(@note), partial: "notes/note", locals: { note: @note, is_selected: true }),
            turbo_stream.replace("editor", partial: "notes/editor", locals: { note: @note })
          ]
        end
      end
    else
      render :index, status: :unprocessable_entity
    end
  end

  def destroy
    @note.destroy

    respond_to do |format|
      format.html do
        next_note = Note.recent.first
        if next_note
          redirect_to note_path(next_note), notice: "笔记已删除"
        else
          redirect_to root_path, notice: "笔记已删除"
        end
      end
      format.turbo_stream do
        render turbo_stream: turbo_stream.remove(dom_id(@note))
      end
    end
  end

  def search
    @query = params[:q]
    @notes = @query.present? ? Note.search(@query).recent : Note.recent
    @note = @notes.first || Note.new

    respond_to do |format|
      format.html { render :index }
      format.turbo_stream do
        render turbo_stream: turbo_stream.replace(
          "note_list",
          partial: "notes/note_list",
          locals: { notes: @notes, selected_note: @note }
        )
      end
    end
  end

  private

  def set_note
    @note = Note.find(params[:id])
  end

  def note_params
    params.require(:note).permit(:title, :content)
  end
end
