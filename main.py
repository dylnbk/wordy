import random
import sys
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, RoundedRectangle
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup


class GameGrid(GridLayout):

    def __init__(self, **kwargs):
        
        # Initialize the parent class
        super().__init__(**kwargs)

        # Set up grid properties
        self.cols = 5
        self.rows = 7
        self.spacing = [10, 10]
        self.padding = [200, 50]
        
        # testing
        Window.maximize()
        
        # Set up letter values
        self.letter_values = {'A': 10, 'B': 35, 'C': 35, 'D': 25, 'E': 10, 'F': 45, 'G': 25, 'H': 45, 'I': 10, 'J': 90, 'K': 55, 'L': 10, 'M': 35, 'N': 10, 'O': 10, 'P': 35, 'Q': 110, 'R': 10, 'S': 10, 'T': 10, 'U': 10, 'V': 45, 'W': 45, 'X': 90, 'Y': 45, 'Z': 110}
        
        # Initialize letter grid
        self.letters = [[random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for col in range(5)] for row in range(7)]
        self.selected_label = None
        self.found_words = []

        # Indexes for special letters
        self.highlighted_letter_index_bonus = random.randint(0, self.rows * self.cols - 1)
        self.highlighted_letter_index_penalty = random.randint(0, self.rows * self.cols - 1)
        self.highlighted_letter_index_reset = random.randint(0, self.rows * self.cols - 1)

        # Ensure special letter indexes are distinct
        while self.highlighted_letter_index_bonus == self.highlighted_letter_index_penalty or self.highlighted_letter_index_bonus == self.highlighted_letter_index_reset:
            self.highlighted_letter_index_bonus = random.randint(0, self.rows * self.cols - 1)

        while self.highlighted_letter_index_penalty == self.highlighted_letter_index_reset:
            self.highlighted_letter_index_penalty = random.randint(0, self.rows * self.cols - 1)

        # Update letter grid
        self.update_letters()

        # Read words from file
        with open('words.txt', 'r') as f:
            self.words = f.read().split()

    def update_letters(self):

        # Clear existing widgets
        self.clear_widgets()

        # Calculate grid and cell sizes
        grid_width, grid_height = self.width - self.padding[0] * 2, self.height - self.padding[1] * 2
        cell_width, cell_height = grid_width / self.cols, grid_height / 7
        font_size = min(cell_width, cell_height) * 0.9

        # Add letter labels to the grid
        for row in range(7):
            for col in range(5):

                letter = self.letters[row][col]

                label = Label(text=letter, font_size=font_size)
                label.bind(on_touch_down=self.on_letter_click)

                # initialize a glow animation for each letter
                label.glow_anim = None  

                # Set color for special letters
                if row * self.cols + col == self.highlighted_letter_index_bonus:
                    label.color = (255, 50, 150)

                if row * self.cols + col == self.highlighted_letter_index_penalty:
                    label.color = (50, 255, 150)

                if row * self.cols + col == self.highlighted_letter_index_reset:
                    label.color = (50, 50, 255)

                # Set row and column for each label
                label.row = row
                label.col = col

                # Add label to the grid
                self.add_widget(label)  

    def reset_grid(self):

        # Clear the letter grid
        self.clear_widgets()

        # Generate new letters for the grid
        self.letters = [[random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for col in range(5)] for row in range(7)]

        # Calculate grid and cell sizes
        grid_width, grid_height = self.width - self.padding[0] * 2, self.height - self.padding[1] * 2
        cell_width, cell_height = grid_width / self.cols, grid_height / 7
        font_size = min(cell_width, cell_height) * 0.8

        # Add new letter labels to the grid
        for row in range(7):
            for col in range(5):

                letter = self.letters[row][col]
                label = Label(text=letter, font_size=font_size)
                label.bind(on_touch_down=self.on_letter_click)
                
                # Initialize a glow animation for each letter
                label.glow_anim = None  

                label.row = row
                label.col = col
                self.add_widget(label)

    def on_letter_click(self, label, touch):

        # Check if the user touched within the bounds of the letter label
        if label.collide_point(*touch.pos):

            # Check for double tap
            if touch.is_double_tap:
                if self.selected_label and self.selected_label == label:
                    # Check if the currently selected letters form a valid word
                    self.check_words()
                    # Reset the currently selected letter
                    self.reset_selected_label()

            else:

                # If a letter is already selected
                if self.selected_label:

                    # Check if the selected letters can be swapped
                    if self.is_valid_swap(self.selected_label, label):
                        # Swap the letters
                        self.swap_letters(self.selected_label, label)
                        # Reset the currently selected letter
                        self.reset_selected_label()

                    else:

                        # Reset the currently selected letter
                        self.reset_selected_label()
                        
                else:

                    # Set the current letter as selected
                    self.selected_label = label

                    # Store the original font size
                    self.font_size = label.font_size  

                    # Increase the font size by 25%
                    label.font_size *= 1.25

                    # Create the shadow animation
                    with label.canvas:

                        color = Color(0, 0, 0, 0.2)
                        label.ellipse = Ellipse(pos=(label.pos[0] - 5, label.pos[1] - 5),
                                                size=(label.size[0] + 10, label.size[1] + 10))
                        animation = Animation(rgba=[0, 0, 0, 0.6], duration=0.5)
                        animation += Animation(rgba=[0, 0, 0, 0.2], duration=0.5)
                        animation.repeat = True
                        animation.start(color)

    def reset_selected_label(self):
        
        # Reset the attributes of the currently selected label
        if self.selected_label:
            
            if self.selected_label.color == [1, 1, 1, 1]:
                
                self.selected_label.font_size = self.font_size  # Set the font size back to the original size
                self.selected_label.color = (1, 1, 1, 1)  # Set the text color back to the original color
                self.selected_label.canvas.remove(self.selected_label.ellipse)  # Remove the shadow animation
                self.selected_label = None
            
            elif self.selected_label.color == [50, 255, 150, 1.0]:

                self.selected_label.font_size = self.font_size  # Set the font size back to the original size
                self.selected_label.color = (50, 255, 150, 1.0)  # Set the text color back to the original color
                self.selected_label.canvas.remove(self.selected_label.ellipse)  # Remove the shadow animation
                self.selected_label = None

            elif self.selected_label.color == [50, 50, 255, 1.0]:

                self.selected_label.font_size = self.font_size  # Set the font size back to the original size
                self.selected_label.color = (50, 50, 255, 1.0)  # Set the text color back to the original color
                self.selected_label.canvas.remove(self.selected_label.ellipse)  # Remove the shadow animation
                self.selected_label = None

            elif self.selected_label.color == [255, 50, 150, 1.0]:

                self.selected_label.font_size = self.font_size  # Set the font size back to the original size
                self.selected_label.color = (255, 50, 150, 1.0)  # Set the text color back to the original color
                self.selected_label.canvas.remove(self.selected_label.ellipse)  # Remove the shadow animation
                self.selected_label = None

    def is_valid_swap(self, label1, label2):

        # Check if two labels are in the same row or the same column
        if label1.row == label2.row or label1.col == label2.col:
            return True
        
        return False

    def on_size(self, *args):

        # Update the letters grid when window size changes
        self.update_letters()

    def swap_letters(self, label1, label2):

        # Swap letters in the grid and update label text
        row1, col1 = label1.row, label1.col
        row2, col2 = label2.row, label2.col
        self.letters[row1][col1], self.letters[row2][col2] = self.letters[row2][col2], self.letters[row1][col1]
        label1.text, label2.text = label2.text, label1.text

        # Update highlighted letter index for bonus if necessary
        if self.highlighted_letter_index_bonus == row1 * self.cols + col1:
            self.highlighted_letter_index_bonus = row2 * self.cols + col2

        elif self.highlighted_letter_index_bonus == row2 * self.cols + col2:
            self.highlighted_letter_index_bonus = row1 * self.cols + col1

        # Update highlighted letter index for penalty if necessary
        if self.highlighted_letter_index_penalty == row1 * self.cols + col1:
            self.highlighted_letter_index_penalty = row2 * self.cols + col2

        elif self.highlighted_letter_index_penalty == row2 * self.cols + col2:
            self.highlighted_letter_index_penalty = row1 * self.cols + col1

        # Update highlighted letter index for reset if necessary
        if self.highlighted_letter_index_reset == row1 * self.cols + col1:
            self.highlighted_letter_index_reset = row2 * self.cols + col2

        elif self.highlighted_letter_index_reset == row2 * self.cols + col2:
            self.highlighted_letter_index_reset = row1 * self.cols + col1

        # Update the letters grid display
        self.update_letters()

    def check_words(self):

        # Check if selected letters form a valid word
        if self.selected_label:

            # Get the row and column of the selected label
            row1, col1 = self.selected_label.row, self.selected_label.col

            # Iterate through each cell in the grid
            for row2 in range(7):
                for col2 in range(5):

                    # Check if current cell is in the same row or column as the selected label
                    if (row1 == row2 and abs(col1 - col2) > 1) or (col1 == col2 and abs(row1 - row2) > 1):

                        # Retrieve the word formed by the selected label and the current cell
                        word = self.get_word(row1, col1, row2, col2)

                        if word in self.found_words:

                            # If the word has already been found, skip
                            pass

                        elif word in self.words:

                            # If the word is in our list of valid words
                            # Get the MyApp instance
                            app = App.get_running_app()

                            # Reset the countdown
                            app.reset_countdown()

                            # Replace the letters with new random letters and update score
                            for row in range(min(row1, row2), max(row1, row2) + 1):
                                for col in range(min(col1, col2), max(col1, col2) + 1):

                                    # Calculate the points for the current letter and replace it with a random letter
                                    points = self.letter_values.get(self.letters[row][col])
                                    self.letters[row][col] = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                                    app.update_score(points)

                            # Initialize variables to check if highlighted letters are used in the current word
                            bonus_used = False
                            penalty_used = False
                            reset_used = False

                            # Check if any of the highlighted letters are used in the current word
                            for row in range(min(row1, row2), max(row1, row2)+1):
                                for col in range(min(col1, col2), max(col1, col2)+1):

                                    if row * self.cols + col == self.highlighted_letter_index_bonus:
                                        bonus_used = True

                                    if row * self.cols + col == self.highlighted_letter_index_penalty:
                                        penalty_used = True

                                    if row * self.cols + col == self.highlighted_letter_index_reset:
                                        reset_used = True

                            # Apply bonus, penalty, or reset effects and update the score
                            total_points = 0

                            if bonus_used and penalty_used:
                                total_points += points
                            elif bonus_used and reset_used:
                                total_points += (points * 2)
                                self.reset_grid()
                            elif penalty_used and reset_used:
                                total_points += (int(points / 2))
                                self.reset_grid()
                            elif bonus_used:
                                total_points += (points * 2)
                            elif penalty_used:
                                total_points += (int(points / 2))
                            elif reset_used:
                                total_points += points
                                self.reset_grid()
                            else:
                                total_points += points

                            app.update_score(total_points)

                            # Add the word to the list of found words
                            self.found_words.append(word)

                            # Generate new indexes for highlighted letters
                            self.highlighted_letter_index_bonus = random.randint(0, self.rows * self.cols - 1)
                            self.highlighted_letter_index_penalty = random.randint(0, self.rows * self.cols - 1)
                            self.highlighted_letter_index_reset = random.randint(0, self.rows * self.cols - 1)

                            # Ensure the new highlighted letter indexes are unique
                            while self.highlighted_letter_index_bonus == self.highlighted_letter_index_penalty or self.highlighted_letter_index_bonus == self.highlighted_letter_index_reset:
                                self.highlighted_letter_index_bonus = random.randint(0, self.rows * self.cols - 1)

                            while self.highlighted_letter_index_penalty == self.highlighted_letter_index_reset:
                                self.highlighted_letter_index_penalty = random.randint(0, self.rows * self.cols - 1)

                            # Update the letters on the grid with new highlighted letters and removed word
                            self.update_letters()


    def get_word(self, row1, col1, row2, col2):

        # Get the word from the grid between two positions (same row or same column)
        word = ""

        if row1 == row2:

            # If the letters are in the same row
            start_col = min(col1, col2)
            end_col = max(col1, col2)

            # Iterate through the row and append characters to the word
            for col in range(start_col, end_col+1):
                word += self.letters[row1][col]

        else:

            # If the letters are in the same column
            start_row = min(row1, row2)
            end_row = max(row1, row2)

            # Iterate through the column and append characters to the word
            for row in range(start_row, end_row+1):
                word += self.letters[row][col1]

        return word
    
class StartMenu(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.app = app

        self.start_button = Button(text="Start", background_color=(0, 0, 0, 0), font_size=42)
        self.how_to_play_button = Button(text="How to play", background_color=(0, 0, 0, 0), font_size=42)
        self.leaderboard_button = Button(text="Leaderboard", background_color=(0, 0, 0, 0), font_size=42)
        self.exit_button = Button(text="Exit", background_color=(0, 0, 0, 0), font_size=42)

        self.start_button.bind(on_press=self.start_game)
        self.how_to_play_button.bind(on_press=self.show_instructions)
        self.leaderboard_button.bind(on_press=self.show_leaderboard)
        self.exit_button.bind(on_press=self.close_app)

        self.add_widget(self.start_button)
        self.add_widget(self.how_to_play_button)
        self.add_widget(self.leaderboard_button)
        self.add_widget(self.exit_button)

    def start_game(self, _):
        game_layout = self.app.build_game_layout()
        game_screen = self.app.sm.get_screen('game')
        game_screen.clear_widgets()  # Clear any existing widgets from the game screen
        game_screen.add_widget(game_layout)  # Add the new game layout
        self.app.sm.current = 'game'

    def show_instructions(self, _):
        instructions = '''
            1. The game will generate random letters.
            2. Your goal is to find as many words as possible using the given letters.
            3. Each word should have at least three letters.
            4. You will get one point for each letter in the word.
            5. Once time runs out, the game is over.
        '''
        popup = Popup(title='How to play',
                      content=Label(text=instructions),
                      size_hint=(0.8, 0.8))
        popup.open()

    def show_leaderboard(self, _):
        # You can customize this method to display the leaderboard scores
        high_score = self.app.high_score
        leaderboard_content = f"Highest Score: {high_score}\n\n1. {high_score}"
        popup = Popup(title='Leaderboard',
                      content=Label(text=leaderboard_content),
                      size_hint=(0.8, 0.8))
        popup.open()

    def close_app(self, _):
        App.get_running_app().stop()
        sys.exit()
        
class MyApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time_left = 30
        self.score = 0
        self.high_score = 0

    def build(self):
        Config.set('graphics', 'fullscreen', 'auto')
        Config.write()

        self.sm = ScreenManager()
        start_menu_screen = Screen(name="start_menu")
        start_menu = StartMenu(self)
        start_menu_screen.add_widget(start_menu)
        self.sm.add_widget(start_menu_screen)

        game_screen = Screen(name="game")
        self.sm.add_widget(game_screen)

        return self.sm

    def build_game_layout(self):
        self.box_layout = BoxLayout(orientation='vertical')

        # Create and configure the score label
        self.score_label = Label(text=f"{self.score}", size_hint=(1, 0.05), font_size=64)

        # Create and configure the gameover label
        self.gameover_label = Label(text=f"", size_hint=(1, 0.05), font_size=36)

        # Create and configure the progress bar
        self.progress_bar = ProgressBar(max=30, value=30, size_hint=(0.4, 0.05), pos_hint={'center_x': 0.5, 'y': 0.01})

        # Create and configure the high score label
        self.high_score_label = Label(text="", size_hint=(1, 0.1), font_size=64)

        # Add the widgets to the box layout
        self.box_layout.add_widget(self.high_score_label)
        self.box_layout.add_widget(self.score_label)
        self.box_layout.add_widget(self.gameover_label)
        self.box_layout.add_widget(self.progress_bar)

        # Create the random letters grid
        self.grid = GameGrid(size_hint=(1, 0.8))
        self.box_layout.add_widget(self.grid)

        # Schedule the count down function to be executed every second
        Clock.schedule_interval(self.count_down, 1)

        return self.box_layout

    def count_down(self, dt):

        self.time_left -= 1
        self.progress_bar.value = self.time_left
        self.gameover_label.halign = 'center'
        self.gameover_label.valign = 'middle'

        if self.time_left == 0:

            # Update the gameover label when the time is up and disable the grid
            self.gameover_label.size_hint = (1, 0.4)
            self.score_label.text = ""
            self.gameover_label.text = "Would you like to play again?"
            self.grid.disabled = True

            # Create the Yes and No buttons
            self.yes_button = Button(text="Yes", size_hint=(1, 0.9), font_size=42, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1))
            self.no_button = Button(text="No", size_hint=(1, 0.9), font_size=42, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1))

            # Bind the buttons to their respective functions
            self.yes_button.bind(on_press=self.restart_game)
            self.no_button.bind(on_press=self.stop_game)

            # Create a box layout for buttons and add the buttons to it
            self.button_box_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
            self.button_box_layout.add_widget(self.yes_button)
            self.button_box_layout.add_widget(self.no_button)

            # Add the button layout to the main layout
            self.box_layout.add_widget(self.button_box_layout)

            # Hide the progress bar
            self.progress_bar.opacity = 0

            # Update the high score if the current score is greater
            if self.score > self.high_score:
                self.high_score = self.score

            return False

    def restart_game(self, instance):
            
            # Reset the score, update the score label and reset the countdown
            self.score = 0
            self.score_label.text = f"{self.score}"
            MyApp.reset_countdown(self)

            # Reset the grid, re-enable it and remove the buttons
            self.grid.reset_grid() 
            Clock.schedule_interval(self.count_down, 1)
            self.grid.disabled = False
            self.box_layout.remove_widget(self.button_box_layout)

            # Update layout sizes and the progress bar
            self.gameover_label.size_hint = (1, 0.05)
            self.progress_bar.value = 30
            self.progress_bar.opacity = 1

    def reset_countdown(self):

        self.time_left = 30  # reset the time_left variable
        self.gameover_label.text = f""  # update the timer label text

    def update_score(self, points):

        # Update the score based on the given points
        self.score += points
        self.score_label.text = f"{self.score}"

    def return_to_menu(self, _):
        self.sm.current = 'start_menu'
        self.grid.reset_grid()
        Clock.unschedule(self.count_down)

        self.box_layout.clear_widgets()
        self.box_layout = None

    def stop_game(self, instance):
        # Create a 'Return to menu' button and bind it to the return_to_menu function
        self.return_to_menu_button = Button(text='Return to menu', size_hint=(1, 0.3), font_size=42, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1))
        self.return_to_menu_button.bind(on_press=self.return_to_menu)

        # Update the high score label and remove unused widgets
        self.high_score_label.text = f"{self.high_score}\n\nGame over"
        self.high_score_label.halign = 'center'
        self.grid.disabled = True
        self.box_layout.remove_widget(self.button_box_layout)

        # Create a new box layout for the game over screen with the same size_hint as the grid
        self.gameover_box = BoxLayout(orientation='vertical', size_hint=(1, 0.8))
        self.anchor_layout = AnchorLayout(anchor_y='top')

        # Remove the high score label from the original parent and add it to the new anchor layout
        self.high_score_label.size_hint = (None, None)
        self.high_score_label.texture_update()
        self.high_score_label.size = self.high_score_label.texture_size
        self.box_layout.remove_widget(self.high_score_label)
        self.anchor_layout.add_widget(self.high_score_label)

        # Add the anchor layout to the gameover box and the return to menu button to the game over screen
        self.gameover_box.add_widget(self.anchor_layout)
        self.gameover_box.add_widget(self.return_to_menu_button)

        # Update the layout based on the user's choice
        if instance.text == "No":
            self.gameover_label.text = ""
            self.box_layout.remove_widget(self.progress_bar)
            self.box_layout.remove_widget(self.grid)

        # Add the gameover_box to the main box layout (replacing the grid)
        self.box_layout.add_widget(self.gameover_box)

    def close_app(self, *args):

        # Stop the running app and exit the system
        App.get_running_app().stop()
        sys.exit()

if __name__ == '__main__':
    MyApp().run()