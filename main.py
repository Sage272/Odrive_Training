import os
import sys
from pickle import GLOBAL

# os.environ['DISPLAY'] = ":0.0"
# os.environ['KIVY_WINDOW'] = 'egl_rpi'

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window, Animation
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen

from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")
from dpea_odrive.odrive_helpers import *

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
TRAJ_SCREEN_NAME = 'traj'
GPIO_SCREEN_NAME = 'gpio'
ADMIN_SCREEN_NAME = 'admin'


class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """

        return SCREEN_MANAGER


Window.clearcolor = (1, 1, 1, 1)  # White

class MainScreen(Screen):
    btn_x = 100
    btn_y = 100
    """
    Class to handle the main screen and its associated touch events
    """

    def rotate_five(self):
        axis1.set_vel(0)
        axis1.wait_for_motor_to_stop()
        axis1.set_pos(axis1.get_pos() + 5)
        axis1.wait_for_motor_to_stop()
        print("Current Position in Turns = ", round(axis1.get_pos(), 2))
        axis1.set_pos(axis1.get_pos() - 5)
        axis1.wait_for_motor_to_stop()
        print("Current Position in Turns = ", round(axis1.get_pos(), 2))

    def adjust_velocity(self):
        #axis1.set_vel(round(self.ids.velocity_slider.value,3)/100 * axis1.get_vel_limit())
        axis1.set_ramped_vel(round(self.ids.velocity_slider.value, 3) / 100 * axis1.get_vel_limit(), round(self.ids.acceleration_slider.value, 3) / 100 * 10)

    def adjust_acceleration(self):
        if round(self.ids.velocity_slider.value, 3) != 0:
            self.adjust_velocity()

    def switch_to_traj(self):
        SCREEN_MANAGER.transition.direction = "left"
        SCREEN_MANAGER.current = TRAJ_SCREEN_NAME

    def switch_to_gpio(self):
        SCREEN_MANAGER.transition.direction = "right"
        SCREEN_MANAGER.current = GPIO_SCREEN_NAME

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'


class TrajectoryScreen(Screen):
    btn_x = 100
    btn_y = 100
    """
    Class to handle the trajectory control screen and its associated touch events
    """

    def trap_traj(self):
        axis1.set_vel(0)
        axis1.wait_for_motor_to_stop()
        accel = self.ids.accel_button_text_input.text
        try:
            accel = float(accel)
        except:
            print("Converting accel to float did not work")
        decel = self.ids.decel_button_text_input.text
        try:
            decel = float(decel)
        except:
            print("Converting decel to float did not work")
        vel = self.ids.velocity_button_text_input.text
        try:
            vel = float(vel)
        except:
            print("Converting vel to float did not work")
        pos = self.ids.pos_button_text_input.text
        try:
            pos = float(pos)
        except:
            print("Converting pos to float did not work")
        try:
            axis1.set_rel_pos_traj(axis1.get_pos() + pos, accel, vel, decel)
        except:
            print("Enter Values")

    def switch_screen(self):
        SCREEN_MANAGER.transition.direction = "right"
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME


class GPIOScreen(Screen):
    btn_x = 100
    btn_y = 100
    """
    Class to handle the GPIO screen and its associated touch/listening events
    """

    def start_GPIO(self):
        if axis1.get_vel() == 0:
            axis1.set_vel(10)
        Clock.schedule_interval(self.read_GPIO_pin, 0.05)

    def read_GPIO_pin(self, dt=0):
        if digital_read(od, 1) == 0:
            Clock.unschedule(self.read_GPIO_pin)
            axis1.set_vel(0)
            axis1.wait_for_motor_to_stop()
            return

    def switch_screen(self):
        SCREEN_MANAGER.transition.direction = "left"
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

class BetterImageButton(ButtonBehavior, Image):
    current_button_id = 0 # static variable to keep track of all buttons
    button_id = 0 # the individual button id
    type = "BetterImageButton"
    def __init__(self, **kwargs):
        """
        Constructor for the better image button
        When using specify : id, source, size, position, on_press, on_release
        :param kwargs: Arguments supplied to super
        """
        super(BetterImageButton, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouseover)
        self.size_hint = None, None
        self.keep_ratio = False
        self.allow_stretch = True
        self.size = 150, 150
        self.background_color = 0, 0, 0, 0
        self.background_normal = ''
        # handles the button_id, each button will have a unique number
        self.button_id = BetterImageButton.current_button_id
        BetterImageButton.current_button_id += 1
        # set the source here for all buttons to have the same image or in you .kv file for a button by button basis
        self.source = "YourImageHere.img"

    # appends the button_id to the end of what self returns to allow for a complete individual reference to each button (the base self return is based off of position, meaning that two buttons could be mixed up)
    def __repr__(self):
        return super(BetterImageButton, self).__repr__() + str(self.button_id)

    # multiplies the two colors together by their individual rgba values
    def multiply_colors(self, color1, color2):
        return (color1[0] * color2[0], color1[1] * color2[1], color1[2] * color2[2], color1[3] * color2[3])


    # the (mouseover_color) or (mouseover_size) at the end shows which mouseover methods use them
    # if there is none, they both use them
    # any (mouseover_color) variable is also use by (mouseover_size) if both are True

    # determines what color to change the button to when hovered over (mouseover_color)
    hover_color = (0.875, 0.875, 0.875, 1.0)
    # SHOULD be set. if not set, the mouseover_size_method will default it to 13/12 the size of the button (mouseover_size)
    hover_size = None
    # determines how long the hover size animation will run (in seconds) (mouseover_size)
    hover_size_anim_duration = 0.125
    # Shouldn't be set, the mouseover methods will handle it (mouseover_color)
    original_color = (0.0, 0.0, 0.0, 0.0)
    # original_size and original_pos shouldn't need to be set because the mouseover_size_method will handle them (mouseover_size)
    # needs to be a large negative number to avoid a None type error (if I used None) or other potential design issues using another, closer to zero number
    original_size = original_pos = [-2147483647, -2147483647]
    # already_hovered is for either method, and handles the one time variable setting
    already_hovered = False
    # on_hover tells whether the button is currently being hovered over or not
    on_hover = False
    # controls whether the color is multiplied, or just set (mouseover_color)
    mouseover_multiply_colors = True
    # can be set to false to remove mouseover capabilities
    mouseover = True
    # determines which mouseover methods should run, one or both can be enabled
    mouseover_color = False
    mouseover_size = False
    # for handling new screens
    current_screen = ""
    previous_screen = ""

    # runs on everytime mouse is with in the window
    def on_mouseover(self, window, pos):
        if self.mouseover:
            # if both mouseover_color and mouseover_size are true, the mouseover_size_method handles that
            # if not, mouseover_size_method still works for just mouseover_size
            # mouseover_color_method works for just mouseover_color
            if self.mouseover_size:
                self.mouseover_size_method(window, pos)
            elif self.mouseover_color:
                self.mouseover_color_method(window, pos)

    def mouseover_color_method(self, window, pos):
        if not self.already_hovered:
            self.already_hovered = True
            self.original_color = self.color
        # runs when the button is being hovered over
        # it runs once, as soon as the cursor is OVER the button
        if not self.on_hover and self.collide_point(*pos):
            self.on_hover = True
            # multiplies the color (or just sets the color) to hover_color
            if self.mouseover_multiply_colors:
                self.color = self.multiply_colors(self.hover_color, self.color)
            else:
                self.color = self.hover_color
        # runs when not hovering over the button
        # it runs once, as soon as the cursor is OFF the button
        elif not self.collide_point(*pos) and self.on_hover:
            self.on_hover = False
            self.color = self.original_color

    def mouseover_size_method(self, widow, pos):
        # runs once per each button, even ones in other screens (than the one fist pulled up)
        # sets values for original_size, hover_size (if one wasn't set), and original_color
        if not self.already_hovered:
            self.already_hovered = True
            self.original_size = [self.size[0], self.size[1]]
            if not self.hover_size:
                self.hover_size = [self.size[0] * (13/12), self.size[1] * (13/12)]
            # for color handling
            # checks if the color should change too, and sets a default value if so
            if self.mouseover_color:
                self.original_color = self.color
        # runs each time a different screen is entered
        if self.current_screen != SCREEN_MANAGER.current:
            self.previous_screen = self.current_screen
            self.current_screen = SCREEN_MANAGER.current
            # ensures that when switching screens, the original_pos does not get set wrongly due to its animation
            # the == [-2147483647, -2147483647] check ensures that the original position is only set once
            # this can't be in the "run once only" if statement because it is on a screen not currently loaded, it will default to [0,0], not its actual position
            if self.original_pos == [-2147483647, -2147483647] and self in SCREEN_MANAGER.current_screen.children: # looking at the new screens children, to see if the new button is in it
                self.original_pos = [self.x, self.y]
        # runs when the button is being hovered over
        # it runs once (because of on_hover), as soon as the cursor is OVER the button
        if not self.on_hover and self.collide_point(*pos):
            self.on_hover = True
            # for color handling
            # checks if the color should change too, and multiplies the color (or just sets the color) to hover_color
            if self.mouseover_color:
                if self.mouseover_multiply_colors:
                    self.color = self.multiply_colors(self.hover_color, self.color)
                else:
                    self.color = self.hover_color
            # animates the button to be the size of hover_size over the course of hover_size_anim_duration
            # the x/y part of the animation keeps the button centered on its original position (necessary because kivy size animations expand from the bottom left out)
            # I use the x/y values here and not center_x/y values, because when I did, the animation was too jittery
            on_hover_anim = Animation(x=(self.x + self.original_size[0]/2) - self.hover_size[0]/2, y=(self.y + self.original_size[1]/2) - self.hover_size[1]/2, size=(self.hover_size[0], self.hover_size[1]), duration=self.hover_size_anim_duration)
            on_hover_anim.start(self)
        # runs when not hovering over the button
        # it runs once (because of on_hover), as soon as the cursor is OFF the button
        elif not self.collide_point(*pos) and self.on_hover:
            self.on_hover = False
            # animates the button back to its original size, while keeping the position centered
            off_hover_anim = Animation(x=self.original_pos[0], y=self.original_pos[1], size=(self.original_size[0], self.original_size[1]), duration=self.hover_size_anim_duration)
            off_hover_anim.start(self)
            # for color handling
            # checks if the color should be changing too, and sets it back to the original color if so
            if self.mouseover_color:
                self.color = self.original_color

class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(
            ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(
            MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()


"""
Widget additions
"""

Builder.load_file('main.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(TrajectoryScreen(name=TRAJ_SCREEN_NAME))
SCREEN_MANAGER.add_widget(GPIOScreen(name=GPIO_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))

"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()

if __name__ == "__main__":
    #send_event("Project Initialized")
    #Window.fullscreen = 'auto'
    run_accel_check_at_start = True
    od = find_odrive("207935A1524B")
    axis1 = ODriveAxis(od.axis1, current_lim=10, vel_lim=25)
    assert od.config.enable_brake_resistor is True, "Check for faulty brake resistor."
    if not axis1.is_calibrated():
        print("calibrating...")
        axis1.calibrate_with_current_lim(10)
    dump_errors(od)
    axis1.set_vel(0)
    axis1.wait_for_motor_to_stop()

    ProjectNameGUI().run()