from abc import ABC, abstractmethod


class StateMachine:
    """
    Represents a state machine. Handles switching between states
    """

    def __init__(self, app):
        self.app = app

        # States
        self.home = HomeState(self.app)

        self.current_state: 'State' = None
        self.prev_state: 'State' = None

    def change_state(self, state: 'State'):
        state.enter()
        self.prev_state, self.current_state = self.current_state, state

    def undo_change(self):
        self.prev_state.enter()
        self.current_state, self.prev_state = self.prev_state, self.current_state


class State(ABC):
    """
    Base state class
    """

    def __init__(self, app):
        self.app = app

    @abstractmethod
    def enter(self):
        ...


class HomeState(State):
    def enter(self):
        self.app.new_file_action.setEnabled(True)
        self.app.open_file_action.setEnabled(True)
        self.app.close_file_action.setEnabled(False)
        self.app.close_all_files_action.setEnabled(False)
        self.app.save_file_action.setEnabled(False)
        self.app.save_file_as_action.setEnabled(False)
        self.app.cut_action.setEnabled(False)
        self.app.copy_action.setEnabled(False)
        self.app.paste_action.setEnabled(False)
        self.app.find_action.setEnabled(False)
        self.app.select_all_action.setEnabled(False)
        self.app.assemble_action.setEnabled(False)
        self.app.play_sim_action.setEnabled(False)
        self.app.step_sim_forward_action.setEnabled(False)
        self.app.step_sim_backwards_action.setEnabled(False)
        self.app.pause_sim_action.setEnabled(False)
        self.app.stop_sim_action.setEnabled(False)
        self.app.reset_sim_action.setEnabled(False)
        self.app.undo_action.setEnabled(False)
        self.app.redo_action.setEnabled(False)


class EditorState(State):
    """
    Editor is open with no changes
    """
    def enter(self):
        self.app.new_file_action.setEnabled(True)
        self.app.open_file_action.setEnabled(True)
        self.app.close_file_action.setEnabled(True)
        self.app.close_all_files_action.setEnabled(True)
        self.app.save_file_action.setEnabled(True)
        self.app.save_file_as_action.setEnabled(True)
        self.app.cut_action.setEnabled(True)
        self.app.copy_action.setEnabled(True)
        self.app.paste_action.setEnabled(True)
        self.app.find_action.setEnabled(True)
        self.app.select_all_action.setEnabled(True)
        self.app.assemble_action.setEnabled(True)
        self.app.play_sim_action.setEnabled(False)
        self.app.step_sim_forward_action.setEnabled(False)
        self.app.step_sim_backwards_action.setEnabled(False)
        self.app.pause_sim_action.setEnabled(False)
        self.app.stop_sim_action.setEnabled(False)
        self.app.reset_sim_action.setEnabled(False)
        self.app.undo_action.setEnabled(False)
        self.app.redo_action.setEnabled(False)

