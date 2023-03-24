import random
import sys
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse
from kivy.uix.progressbar import ProgressBar


class RandomLettersGrid(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 5
        self.spacing = [10, 10]
        self.padding = [50, 50]
        self.letter_values = {'A': 10, 'B': 35, 'C': 35, 'D': 25, 'E': 10, 'F': 45, 'G': 25, 'H': 45, 'I': 10, 'J': 90, 'K': 55, 'L': 10, 'M': 35, 'N': 10, 'O': 10, 'P': 35, 'Q': 110, 'R': 10, 'S': 10, 'T': 10, 'U': 10, 'V': 45, 'W': 45, 'X': 90, 'Y': 45, 'Z': 110}
        self.letters = [[random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for col in range(5)] for row in range(7)]
        self.update_letters()
        self.selected_label = None
        self.words =["CAT", "DOG", "HEY", "BOB", "CAR", "HAT", "SUN", "MOON", "RAIN", "SNOW", "FIRE", "ICE", 
         "FOOD", "WORK", "PLAY", "REST", "LOVE", "HOME", "MIND", "BODY", "SOUL", "MUSIC", 
         "ART", "BOOK", "PARK", "CITY", "TOWN", "GAME", "TEAM", "FILM", "SHOW", "TIME", 
         "JOY", "FARM", "TREE", "BIRD", "DEER", "FISH", "SHIP", "WIND", "WAVE", "SAND", 
         "HERO", "GOLD", "WINE", "HAIL", "SNAP", "LEAF", "FOOT", "HAND", "FACE", "HAIR"]
        self.found_words = []

    def on_size(self, *args):
        self.update_letters()

    def update_letters(self):
        self.clear_widgets()
        grid_width, grid_height = self.width - self.padding[0] * 2, self.height - self.padding[1] * 2
        cell_width, cell_height = grid_width / self.cols, grid_height / 7
        font_size = min(cell_width, cell_height) * 0.8
        for row in range(7):
            for col in range(5):
                letter = self.letters[row][col]
                label = Label(text=letter, font_size=font_size)
                label.bind(on_touch_down=self.on_letter_click)
                label.glow_anim = None  # initialize a glow animation for each letter
                label.row = row
                label.col = col
                self.add_widget(label)

    def reset_grid(self):
        self.clear_widgets()
        self.letters = [[random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for col in range(5)] for row in range(7)]
        grid_width, grid_height = self.width - self.padding[0] * 2, self.height - self.padding[1] * 2
        cell_width, cell_height = grid_width / self.cols, grid_height / 7
        font_size = min(cell_width, cell_height) * 0.8
        for row in range(7):
            for col in range(5):
                letter = self.letters[row][col]
                label = Label(text=letter, font_size=font_size)
                label.bind(on_touch_down=self.on_letter_click)
                label.glow_anim = None  # initialize a glow animation for each letter
                label.row = row
                label.col = col
                self.add_widget(label)

    def on_letter_click(self, label, touch):
        if label.collide_point(*touch.pos):
            if touch.is_double_tap:
                self.check_words()
            else:
                
                if self.selected_label:
                    if self.is_valid_swap(self.selected_label, label):
                        self.swap_letters(self.selected_label, label)
                        self.selected_label.font_size = self.font_size  # set the font size back to the original size
                        self.selected_label.text_color = (1, 1, 1, 1)  # set the text color back to the original color
                        self.selected_label.canvas.remove(self.selected_label.ellipse)  # remove the shadow animation
                        self.selected_label = None
                    else:
                        self.selected_label.font_size = self.font_size  # set the font size back to the original size
                        self.selected_label.text_color = (1, 1, 1, 1)  # set the text color back to the original color
                        self.selected_label.canvas.remove(self.selected_label.ellipse)  # remove the shadow animation
                        self.selected_label = None
                else:
                    self.selected_label = label
                    self.font_size = label.font_size  # store the original font size
                    label.font_size *= 1.2  # increase the font size by 20%
                    label.text_color = (1.2, 1.2, 1.2, 1)  # set the text color to indicate it's selected
                    
                    # create the shadow animation
                    with label.canvas:
                        color = Color(0, 0, 0, 0.2)
                        label.ellipse = Ellipse(pos=(label.pos[0]-5, label.pos[1]-5), size=(label.size[0]+10, label.size[1]+10))
                        animation = Animation(rgba=[0, 0, 0, 0.6], duration=0.5)
                        animation += Animation(rgba=[0, 0, 0, 0.2], duration=0.5)
                        animation.repeat = True
                        animation.start(color)

    def is_valid_swap(self, label1, label2):
        if label1.row == label2.row or label1.col == label2.col:
            return True
        return False


    def swap_letters(self, label1, label2):
        row1, col1 = label1.row, label1.col
        row2, col2 = label2.row, label2.col
        self.letters[row1][col1], self.letters[row2][col2] = self.letters[row2][col2], self.letters[row1][col1]
        label1.text, label2.text = label2.text, label1.text
        self.update_letters()

    def check_words(self):
        
        if self.selected_label:
            row1, col1 = self.selected_label.row, self.selected_label.col
            for row2 in range(7):
                for col2 in range(5):
                    if (row1 == row2 and abs(col1 - col2) > 1) or (col1 == col2 and abs(row1 - row2) > 1):
                        word = self.get_word(row1, col1, row2, col2)
                        if word in self.words:
                            # Get the MyApp instance
                            app = App.get_running_app()

                            # Reset the countdown
                            app.reset_countdown()

                            # Replace the letters with new random letters
                            for row in range(min(row1, row2), max(row1, row2)+1):
                                for col in range(min(col1, col2), max(col1, col2)+1):
                                    points = self.letter_values.get(self.letters[row][col])
                                    app.update_score(points)
                                    self.letters[row][col] = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                            
                            self.update_letters()

    def get_word(self, row1, col1, row2, col2):
        word = ""
        if row1 == row2:
            # if the letters are in the same row
            start_col = min(col1, col2)
            end_col = max(col1, col2)
            for col in range(start_col, end_col+1):
                word += self.letters[row1][col]
        else:
            # if the letters are in the same column
            start_row = min(row1, row2)
            end_row = max(row1, row2)
            for row in range(start_row, end_row+1):
                word += self.letters[row][col1]
        return word
        
class MyApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time_left = 30
        self.score = 0
        self.high_score = 0
        self.box_layout = BoxLayout(orientation='vertical')

    def build(self):

        self.score_label = Label(text=f"Score: {self.score}", size_hint=(1, 0.05), font_size=24)
        
        self.gameover_label = Label(text=f"", size_hint=(1, 0.05), font_size=24)
        self.progress_bar = ProgressBar(max=30, value=30, size_hint=(0.8, 0.05), pos_hint={'center_x': 0.5, 'y': 0.01})
        
        self.high_score_label = Label(text="", size_hint=(1, 0.1), font_size=24)

        
        self.box_layout.add_widget(self.high_score_label)
        self.box_layout.add_widget(self.score_label)
        self.box_layout.add_widget(self.gameover_label)
        self.box_layout.add_widget(self.progress_bar)

        self.grid = RandomLettersGrid(size_hint=(1, 0.8))
        self.box_layout.add_widget(self.grid)

        Clock.schedule_interval(self.count_down, 1)

        return self.box_layout

    def count_down(self, dt):
        self.time_left -= 1
        self.progress_bar.value = self.time_left
        self.gameover_label.halign = 'center'
        self.gameover_label.valign = 'middle'
        if self.time_left == 0:
            self.gameover_label.size_hint = (1, 0.4)
            self.score_label.text = ""
            self.gameover_label.text = "Game over\nWould you like to play again?"
            self.grid.disabled = True
            self.yes_button = Button(text="Yes", size_hint=(1, 0.5), font_size=24, background_color=(0.5, 0.5, 0.5, 0.8), color=(1, 1, 1, 1))
            self.no_button = Button(text="No", size_hint=(1, 0.5), font_size=24, background_color=(0.5, 0.5, 0.5, 0.8), color=(1, 1, 1, 1))
            self.yes_button.bind(on_press=self.restart_game)
            self.no_button.bind(on_press=self.stop_game)
            self.button_box_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
            self.button_box_layout.add_widget(self.yes_button)
            self.button_box_layout.add_widget(self.no_button)
            self.box_layout.add_widget(self.button_box_layout)
            self.progress_bar.opacity = 0

            if self.score > self.high_score:
                self.high_score = self.score

            return False

    def restart_game(self, instance):
        self.score = 0
        self.score_label.text = f"Score: {self.score}"
        MyApp.reset_countdown(self)
        self.grid.reset_grid() 
        Clock.schedule_interval(self.count_down, 1)
        self.grid.disabled = False
        self.box_layout.remove_widget(self.button_box_layout)
        self.gameover_label.size_hint = (1, 0.05)
        self.progress_bar.value = 30
        self.progress_bar.opacity = 1

    def reset_countdown(self):
        self.time_left = 30  # reset the time_left variable
        self.gameover_label.text = f""  # update the timer label text

    def update_score(self, points):
        self.score += points
        self.score_label.text = f"Score: {self.score}"

    def stop_game(self, instance):
        # Add a 'Close' button
        self.close_button = Button(text='Exit', size_hint=(1, 0.1), font_size=24, background_color=(0.5, 0.5, 0.5, 0.8), color=(1, 1, 1, 1))
        self.close_button.bind(on_press=self.close_app)

        self.box_layout.remove_widget(self.score_label)
        self.high_score_label.text = f"High score: {self.high_score}"
        self.high_score_label.size_hint = (1, 0.5)
        self.high_score_label.halign = 'center'
        self.high_score_label.valign = 'middle'
        self.high_score_label.text += f"\n\nThanks for playing!"
        self.grid.disabled = True
        self.box_layout.remove_widget(self.button_box_layout)
        if instance.text == "No":
            self.gameover_label.text = ""
            self.box_layout.remove_widget(self.progress_bar)
            self.box_layout.remove_widget(self.grid)

        # Add the 'Close' button to the app
        self.box_layout.add_widget(self.close_button)
        return False
    
    def close_app(self, *args):
        App.get_running_app().stop()
        sys.exit()

if __name__ == '__main__':
    MyApp().run()