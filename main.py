import random
import sys
import requests
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
from kivy.uix.floatlayout import FloatLayout


def calculate_font_size(screen_width, screen_height, size):
  # Calculate the font size based on the screen width and height.
  font_size = min(screen_width / size, screen_height / size)
  return font_size

def get_random_words(filename, num_words=5):

  try:
    with open(filename, "r") as f:
      words = f.read().split()
      if len(words) < num_words:
        raise ValueError("File does not contain enough words")
      random_words = random.sample(words, num_words)
      return [word.capitalize() for word in random_words]
  except FileNotFoundError:
    print(f"Error: File '{filename}' not found")
    return None
  except ValueError as e:
    print(e)
    return None
  
def daily_words(words):

    daily_words = ''

    for ix, word in enumerate(words, 1):
        daily_words += f"\n{word}"

    return daily_words

class ServerItems():

    def get_daily_challenge():
        response = requests.get("http://localhost:5000/daily_challenge")
        if response.status_code == 200:
            daily_word = response.json()["daily_words"]
            return daily_word
        else:
            return None

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
        font_size = min(cell_width, cell_height) * 0.9

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
        
        self.update_letters()

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

                            points = 0

                            # Replace the letters with new random letters and update score
                            for row in range(min(row1, row2), max(row1, row2) + 1):
                                for col in range(min(col1, col2), max(col1, col2) + 1):

                                    # Calculate the points for the current letter and replace it with a random letter
                                    points += self.letter_values.get(self.letters[row][col])
                                    self.letters[row][col] = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

                            # Initialize variables to check if highlighted letters are used in the current word
                            bonus_used = False
                            word_bonus = False
                            penalty_used = False
                            reset_used = False
                            word = word.capitalize()

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
                                self.reset_grid()
                            elif bonus_used:
                                total_points += (points * 2)
                            elif reset_used:
                                total_points += points
                                self.reset_grid()
                            else:
                                if word in bonus_words:
                                    total_points += points
                                    word_bonus = True
                                    bonus_words.remove(word)
                                else:
                                    total_points += points

                            app.update_score(total_points, penalty_used, word_bonus)

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

        self.start_button = Button(text="Start", background_color=(0, 0, 0, 0), font_size=font_size_medium)
        self.how_to_play_button = Button(text="How to play", background_color=(0, 0, 0, 0), font_size=font_size_medium)
        self.bonus_button = Button(text="Bonus", background_color=(0, 0, 0, 0), font_size=font_size_medium)
        self.exit_button = Button(text="Exit", background_color=(0, 0, 0, 0), font_size=font_size_medium)

        self.start_button.bind(on_press=self.start_game)
        self.how_to_play_button.bind(on_press=self.show_instructions)
        self.bonus_button.bind(on_press=self.show_bonus)
        self.exit_button.bind(on_press=self.close_app)

        self.add_widget(self.start_button)
        self.add_widget(self.how_to_play_button)
        self.add_widget(self.bonus_button)
        self.add_widget(self.exit_button)

    def start_game(self, _):
        game_layout = self.app.build_game_layout()
        game_screen = self.app.sm.get_screen('game')
        game_screen.clear_widgets()  # Clear any existing widgets from the game screen
        game_screen.add_widget(game_layout)  # Add the new game layout
        self.app.sm.current = 'game'

    def show_instructions(self, _):

        instructions = '''
            • Tap on a letter to move its position and create words.

            • Each word should have at least three letters.

            • Double tap the last letter of your word to submit and score points.

            • Including a [color=32FF96]green[/color] letter will double the word score.

            • Including a [color=FF3296]red[/color] letter will lose half the total score.

            • Including a [color=FFFF32]yellow[/color] letter will generate a new letter grid.

            • Submit a word from the bonus list to double the total score.

            • The same word cannot be submitted twice.

            • Once the time runs out, the game is over!
        '''

        # create layout
        layout = BoxLayout(orientation='vertical')

        # create label and add to layout
        label = Label(text=instructions, font_size=font_size_medium, markup=True)  # this line is updated
        layout.add_widget(label)

        # create button and add to layout
        button = Button(text='Back', size_hint=(1, 0.5), font_size=font_size_medium, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1))
        layout.add_widget(button)

        popup = Popup(content=layout,  # set content as layout
                    size_hint=(0.8, 0.8),
                    title_size=0, 
                    separator_height=0)

        popup.background = ''
        popup.background_color = (0, 0, 0)

        # bind button on_release to popup.dismiss
        button.bind(on_release=popup.dismiss)

        popup.open()

    def show_bonus(self, _):
        bonus_content = f"Submit a word from the list to double your current total:\n\n{daily_words(bonus_words)}"
        label = Label(text=bonus_content, font_size=font_size_medium, halign='center')
        button = Button(text='Back', size_hint=(1, 0.08), font_size=font_size_medium, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1))

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(label)
        layout.add_widget(button)

        popup = Popup(content=layout, size_hint=(1, 1), title_size=0, separator_height=0)
        popup.background = ''
        popup.background_color = (0, 0, 0)

        button.bind(on_release=popup.dismiss)

        popup.open()
    
    '''
    def show_leaderboard(self, _):
        
        high_score = self.app.high_score
        leaderboard_content = f"Highest Score: {high_score}\n\n1. {high_score}"
        popup = Popup(content=Label(text=leaderboard_content, font_size=font_size_medium),
                    size_hint=(0.8, 0.8),
                    title_size=0, 
                    separator_height=0)
        popup.background = ''
        popup.background_color = (0, 0, 0)

        popup.open()
    '''

    def close_app(self, _):
        App.get_running_app().stop()
        sys.exit()

class BurgerButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = '='
        self.size_hint = (0.1, 0.1)
        self.pos_hint = {'x': 0, 'top': 1}
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)  # adjust color properties as needed
        self.font_size = font_size_large
        self.opacity = 0
        self.disabled = True

class InfoButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = 'Bonus'
        self.size_hint = (0.1, 0.1)
        self.pos_hint = {'right': 1, 'top': 1}
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)  # adjust color properties as needed
        self.font_size = font_size_large
        self.opacity = 0
        self.disabled = True
        
class MyApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.countdown_event = None
        self.time_left = 30
        self.score = 0
        self.high_score = 0
        self.menu_popup = Popup(content=self.build_menu_layout(),
                                    background_color=(0, 0, 0),
                                    size_hint=(1, 1),
                                    title_size=0, 
                                    separator_height=0)

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

        self.float_layout = FloatLayout()

        # Create burger button
        self.burger_button = BurgerButton()
        self.burger_button.bind(on_release=self.open_menu)

        # Create info button
        self.info_button = InfoButton()
        self.info_button.bind(on_release=self.open_info)

        # Add the screen manager and the burger button to the float layout
        self.float_layout.add_widget(self.sm)    # your ScreenManager
        self.float_layout.add_widget(self.info_button)
        self.float_layout.add_widget(self.burger_button)

        return self.float_layout


    def open_info(self, instance):
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=daily_words(bonus_words), font_size=font_size_large))
        close_button = Button(text="X", size_hint=(1, 0.2), font_size=font_size_medium, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1))
        box.add_widget(close_button)

        self.info_popup = Popup(content=box,
                            background_color=(0, 0, 0),
                            size_hint=(1, 1),
                            title_size=0, 
                            separator_height=0)

        close_button.bind(on_release=self.info_popup.dismiss)
        self.info_popup.bind(on_dismiss=self.on_info_popup_dismiss)

        Clock.unschedule(self.count_down)
        self.info_popup.open()

    def on_info_popup_dismiss(self, *args):
        Clock.schedule_interval(self.count_down, 1)

    def show_info_menu(self):
        self.info_button.opacity = 1
        self.info_button.disabled = False

    def hide_info_menu(self):
        self.info_button.opacity = 0
        self.info_button.disabled = True
    
    def show_burger_menu(self):
        self.burger_button.opacity = 1
        self.burger_button.disabled = False

    def hide_burger_menu(self):
        self.burger_button.opacity = 0
        self.burger_button.disabled = True

    def build_game_layout(self):
        self.box_layout = BoxLayout(orientation='vertical')

        # Create and configure the score label
        self.score_label = Label(text=f"{self.score}", size_hint=(1, 0.05), font_size=font_size_large)

        # Create and configure the gameover label
        self.gameover_label = Label(text=f"", size_hint=(1, 0.05), font_size=font_size_small)

        # Create and configure the progress bar
        self.progress_bar = ProgressBar(max=30, value=30, size_hint=(0.4, 0.05), pos_hint={'center_x': 0.5, 'y': 0.01})

        # Create and configure the high score label
        self.high_score_label = Label(text="", size_hint=(1, 0.1), font_size=font_size_large)

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

        # Show the burger menu
        self.show_burger_menu()

        self.show_info_menu()

        return self.box_layout
    
    def open_menu(self, instance):
        self.menu_popup.open()
        Clock.unschedule(self.count_down)

    def build_menu_layout(self):
        box = BoxLayout(orientation='vertical')
        resume_button = Button(text='Resume', font_size=font_size_medium, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1))
        resume_button.bind(on_press=self.close_menu)
        restart_button = Button(text='Restart', font_size=font_size_medium, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1))
        restart_button.bind(on_press=self.restart_game)
        exit_button = Button(text='Exit', font_size=font_size_medium, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1))
        exit_button.bind(on_press=self.close_app)
        box.add_widget(resume_button)
        box.add_widget(restart_button)
        box.add_widget(exit_button)
        return box

    def close_menu(self, instance):
        self.menu_popup.dismiss()
        Clock.schedule_interval(self.count_down, 1)

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
            self.yes_button = Button(text="Yes", size_hint=(1, 0.9), font_size=font_size_medium, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1))
            self.no_button = Button(text="No", size_hint=(1, 0.9), font_size=font_size_medium, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1))

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

        global bonus_words

        bonus_words = get_random_words("words.txt")

        # Reset the score, update the score label and reset the countdown
        self.score = 0
        self.score_label.text = f"{self.score}"

        self.menu_popup.dismiss()
        self.reset_countdown()

        if self.countdown_event:
            Clock.unschedule(self.countdown_event)
        self.countdown_event = Clock.schedule_interval(self.count_down, 1)

        # Reset the grid, re-enable it and check if button_box_layout exists before removing it
        self.grid.reset_grid() 
        self.grid.disabled = False
        if hasattr(self, 'button_box_layout'):
            self.box_layout.remove_widget(self.button_box_layout)

        # Update layout sizes and the progress bar
        self.gameover_label.size_hint = (1, 0.05)
        self.progress_bar.value = 30
        self.progress_bar.opacity = 1

    def reset_countdown(self):

        self.time_left = 30  # reset the time_left variable
        self.gameover_label.text = f""  # update the timer label text

    def update_score(self, points, penalty, word_bonus):

        if penalty:
            if self.score <= 1:
                self.score = 0
            else:
                self.score = int(self.score / 2)
        elif word_bonus:
            self.score *= 2
        else:
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
        self.return_to_menu_button = Button(text='Exit', size_hint=(1, 0.3), font_size=font_size_medium, background_color=(0, 0, 0, 0), color=(1, 1, 1, 1))
        self.return_to_menu_button.bind(on_press=self.close_app)

        self.info_button.opacity = 0
        self.burger_button.opacity = 0

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

    global bonus_words

    # Font sizes
    font_size_large = calculate_font_size(Window.width, Window.height, 32)
    font_size_medium = calculate_font_size(Window.width, Window.height, 42)
    font_size_small = calculate_font_size(Window.width, Window.height, 62)

    bonus_words = get_random_words("words.txt")

    # Run app
    MyApp().run()