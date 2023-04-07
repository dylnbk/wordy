<!--

Step 2: Create a simple Flask app Create a new Python file, let's call it app.py, and add the following code:

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/daily_challenge', methods=['GET'])
def daily_challenge():
    daily_word = "example"  # Replace with your daily word selection logic
    return jsonify({"daily_word": daily_word})

if __name__ == '__main__':
    app.run(debug=True)
This code will create a simple Flask app with a single /daily_challenge route that returns a JSON object containing the daily challenge word.

Step 3: Run your Flask app Navigate to the directory containing your app.py file, and run the following command:


python app.py
By default, the Flask app will start on port 5000. Open your web browser and go to http://localhost:5000/daily_challenge to see the response.

Step 4: Integrate the Flask API with your game

In your word game, add a function that retrieves the daily challenge word from your Flask app:


import requests

def get_daily_challenge():
    response = requests.get("http://localhost:5000/daily_challenge")
    if response.status_code == 200:
        daily_word = response.json()["daily_word"]
        return daily_word
    else:
        return None
Now, you can call this get_daily_challenge() function in your game to fetch the daily challenge from the server (your Flask app) and use the word accordingly.

Remember, this is a very basic setup meant for local testing, and you'll need to deploy the Flask app to a server to make it accessible to other players. There are numerous hosting services, like Heroku, PythonAnywhere, or a Virtual Private Server (VPS) that allow you to deploy Flask apps easily.

-->


class StartScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        self.play_button = Button(text="Play", font_size=24)
        self.play_button.bind(on_press=self.start_game)

        self.rules_button = Button(text="Rules", font_size=24)
        self.rules_button.bind(on_press=self.show_rules)

        self.stats_button = Button(text="Statistics", font_size=24)
        self.stats_button.bind(on_press=self.show_stats)

        self.menu_layout.add_widget(self.play_button)
        self.menu_layout.add_widget(self.rules_button)
        self.menu_layout.add_widget(self.stats_button)

        self.add_widget(self.menu_layout)

    def start_game(self, instance):
        self.manager.current = "game_screen"

    def show_rules(self, instance):
        print("Showing rules...")  # You can implement the rules screen here

    def show_stats(self, instance):
        print("Showing stats...")  # You can implement the stats screen here


class GameScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time_left = 30
        self.score = 0
        self.high_score = 0
        self.box_layout = BoxLayout(orientation='vertical')

    def build(self):

        self.score_label = Label(text=f"{self.score}", size_hint=(1, 0.05), font_size=24)
        
        self.gameover_label = Label(text=f"", size_hint=(1, 0.05), font_size=24)
        self.progress_bar = ProgressBar(max=30, value=30, size_hint=(0.4, 0.05), pos_hint={'center_x': 0.5, 'y': 0.01})
        
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
            self.gameover_label.text = "Would you like to play again?"
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
        self.score_label.text = f"{self.score}"
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
        self.score_label.text = f"{self.score}"

    def stop_game(self, instance):
        # Add a 'Close' button
        self.close_button = Button(text='Exit', size_hint=(1, 0.1), font_size=24, background_color=(0.5, 0.5, 0.5, 0.8), color=(1, 1, 1, 1))
        self.close_button.bind(on_press=self.close_app)

        self.box_layout.remove_widget(self.score_label)
        self.high_score_label.text = f"{self.high_score}"
        self.high_score_label.size_hint = (1, 0.5)
        self.high_score_label.halign = 'center'
        self.high_score_label.valign = 'middle'
        self.high_score_label.text += f"\n\nGame over"
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


class MyApp(App):

    def build(self):
        self.screen_manager = ScreenManager()

        self.start_screen = StartScreen(name="start_screen")
        self.game_screen = GameScreen(name="game_screen")

        self.screen_manager.add_widget(self.start_screen)
        self.screen_manager.add_widget(self.game_screen)

        return self.screen_manager


if __name__ == '__main__':
    MyApp().run()