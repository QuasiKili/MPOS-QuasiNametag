from mpos.apps import Activity
import mpos.ui
import mpos.ui.anim
import mpos.ui.focus_direction
import lvgl as lv

class QuasiNametag(Activity):

    # State variables
    name_text = "Your Name"
    fg_color = 0xFFFFFF  # White
    bg_color = 0x000000  # Black
    is_editing = True

    # Widgets
    edit_screen = None
    display_screen = None
    name_ta = None
    keyboard = None
    confirm_button = None
    fg_color_buttons = []
    bg_color_buttons = []
    display_label = None

    # Color palette (common colors)
    colors = [
        {"name": "Black", "value": 0x000000},
        {"name": "White", "value": 0xFFFFFF},
        {"name": "Red", "value": 0xFF0000},
        {"name": "Green", "value": 0x00FF00},
        {"name": "Blue", "value": 0x0000FF},
        {"name": "Yellow", "value": 0xFFFF00},
        {"name": "Cyan", "value": 0x00FFFF},
        {"name": "Magenta", "value": 0xFF00FF},
    ]

    def onCreate(self):
        # Create a container to hold both screens
        container = lv.obj()
        container.set_style_pad_all(0, 0)

        # Add key event handler to container to catch all key events
        container.add_event_cb(self.global_key_handler, lv.EVENT.KEY, None)

        # Create both screens as children of the container
        self.create_edit_screen(container)
        self.create_display_screen(container)

        # Hide edit screen initially, show display screen
        self.edit_screen.add_flag(lv.obj.FLAG.HIDDEN)
        self.is_editing = False

        # Update display with initial values
        self.update_display_screen()

        # Set the container as content view (only call this once)
        self.setContentView(container)

        # Set focus to display screen so it receives key events on initial load
        focusgroup = lv.group_get_default()
        if focusgroup:
            mpos.ui.focus_direction.emulate_focus_obj(focusgroup, self.display_screen)

    def create_edit_screen(self, parent):
        self.edit_screen = lv.obj(parent)
        self.edit_screen.set_size(lv.pct(100), lv.pct(100))
        self.edit_screen.set_style_pad_all(8, 0)

        # Title
        title = lv.label(self.edit_screen)
        title.set_text("Nametag Editor")
        title.align(lv.ALIGN.TOP_MID, 0, 5)
        title.set_style_text_font(lv.font_montserrat_16, 0)

        # Name input textarea (slightly narrower to make room for clear button)
        self.name_ta = lv.textarea(self.edit_screen)
        self.name_ta.set_width(lv.pct(70))
        self.name_ta.set_one_line(True)
        self.name_ta.set_text(self.name_text)
        self.name_ta.align(lv.ALIGN.TOP_LEFT, 22, 50)
        self.name_ta.add_event_cb(lambda *args: self.show_keyboard(), lv.EVENT.CLICKED, None)

        # Clear button (X) next to name field
        clear_btn = lv.button(self.edit_screen)
        clear_btn.set_size(30, 30)
        clear_btn.align_to(self.name_ta, lv.ALIGN.OUT_RIGHT_MID, 5, 0)
        clear_btn.add_event_cb(self.clear_name, lv.EVENT.CLICKED, None)
        clear_label = lv.label(clear_btn)
        clear_label.set_text(lv.SYMBOL.CLOSE)
        clear_label.center()

        # Name label - aligned to textarea
        name_label = lv.label(self.edit_screen)
        name_label.set_text("Name:")
        name_label.align_to(self.name_ta, lv.ALIGN.OUT_TOP_LEFT, 0, -5)

        # Foreground color container - centered independently
        fg_cont = lv.obj(self.edit_screen)
        fg_cont.set_size(lv.pct(85), 32)
        fg_cont.align(lv.ALIGN.TOP_MID, 0, 115)
        fg_cont.set_flex_flow(lv.FLEX_FLOW.ROW)
        fg_cont.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        fg_cont.set_style_pad_all(3, 0)

        # Foreground label - aligned to color container
        fg_label = lv.label(self.edit_screen)
        fg_label.set_text("Text Color:")
        fg_label.align_to(fg_cont, lv.ALIGN.OUT_TOP_LEFT, 0, -5)

        # Create color buttons for foreground
        self.fg_color_buttons = []
        for color in self.colors:
            btn = lv.button(fg_cont)
            btn.set_size(16, 16)
            btn.set_style_bg_color(lv.color_hex(color["value"]), 0)
            btn.set_style_radius(5, 0)
            btn.add_event_cb(lambda e, c=color["value"]: self.set_fg_color(c), lv.EVENT.CLICKED, None)
            self.fg_color_buttons.append(btn)

        # Background color container - centered and positioned below fg_cont
        bg_cont = lv.obj(self.edit_screen)
        bg_cont.set_size(lv.pct(85), 32)
        bg_cont.align_to(fg_cont, lv.ALIGN.OUT_BOTTOM_MID, 0, 30)
        bg_cont.set_flex_flow(lv.FLEX_FLOW.ROW)
        bg_cont.set_flex_align(lv.FLEX_ALIGN.SPACE_EVENLY, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        bg_cont.set_style_pad_all(3, 0)

        # Background label - aligned to color container
        bg_label = lv.label(self.edit_screen)
        bg_label.set_text("Background:")
        bg_label.align_to(bg_cont, lv.ALIGN.OUT_TOP_LEFT, 0, -5)

        # Create color buttons for background
        self.bg_color_buttons = []
        for color in self.colors:
            btn = lv.button(bg_cont)
            btn.set_size(16, 16)
            btn.set_style_bg_color(lv.color_hex(color["value"]), 0)
            btn.set_style_radius(5, 0)
            btn.add_event_cb(lambda e, c=color["value"]: self.set_bg_color(c), lv.EVENT.CLICKED, None)
            self.bg_color_buttons.append(btn)

        # Confirm button - positioned below background colors and centered
        self.confirm_button = lv.button(self.edit_screen)
        self.confirm_button.set_size(lv.pct(85), 40)
        self.confirm_button.align_to(bg_cont, lv.ALIGN.OUT_BOTTOM_MID, 0, 20)
        self.confirm_button.add_event_cb(self.confirm_and_show_display, lv.EVENT.CLICKED, None)
        confirm_label = lv.label(self.confirm_button)
        confirm_label.set_text("Show Nametag")
        confirm_label.center()

        # Keyboard (hidden by default)
        self.keyboard = lv.keyboard(self.edit_screen)
        self.keyboard.align(lv.ALIGN.BOTTOM_MID, 0, 0)
        self.keyboard.set_textarea(self.name_ta)
        self.keyboard.set_style_max_height(120, 0)
        self.keyboard.add_event_cb(lambda *args: self.hide_keyboard(), lv.EVENT.READY, None)
        self.keyboard.add_event_cb(lambda *args: self.hide_keyboard(), lv.EVENT.CANCEL, None)
        self.keyboard.add_flag(lv.obj.FLAG.HIDDEN)

    def create_display_screen(self, parent):
        self.display_screen = lv.obj(parent)
        self.display_screen.set_size(lv.pct(100), lv.pct(100))
        self.display_screen.set_style_pad_all(0, 0)

        # Remove border and outline
        self.display_screen.set_style_border_width(0, 0)
        self.display_screen.set_style_outline_width(0, 0)
        self.display_screen.set_style_radius(0, 0)

        # Make the entire display screen clickable to return to edit mode
        self.display_screen.add_flag(lv.obj.FLAG.CLICKABLE)
        self.display_screen.add_event_cb(self.show_edit_screen, lv.EVENT.CLICKED, None)

        # Add to focus group so it can receive key events
        focusgroup = lv.group_get_default()
        if focusgroup:
            focusgroup.add_obj(self.display_screen)

        # Debug: print all events
        self.display_screen.add_event_cb(lambda e: mpos.ui.print_event(e), lv.EVENT.ALL, None)

        # Create a label for displaying the name
        self.display_label = lv.label(self.display_screen)
        self.display_label.set_long_mode(lv.label.LONG_MODE.CLIP)
        self.display_label.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)

    def show_keyboard(self):
        self.confirm_button.add_flag(lv.obj.FLAG.HIDDEN)
        mpos.ui.anim.smooth_show(self.keyboard)
        focusgroup = lv.group_get_default()
        if focusgroup:
            focusgroup.focus_next()

    def hide_keyboard(self):
        mpos.ui.anim.smooth_hide(self.keyboard)
        self.confirm_button.remove_flag(lv.obj.FLAG.HIDDEN)

    def clear_name(self, event):
        self.name_ta.set_text("")

    def set_fg_color(self, color):
        self.fg_color = color
        print(f"Foreground color set to: {hex(color)}")
        self.update_color_indicators()

    def set_bg_color(self, color):
        self.bg_color = color
        print(f"Background color set to: {hex(color)}")
        self.update_color_indicators()

    def update_color_indicators(self):
        # Update foreground color buttons
        for i, color_info in enumerate(self.colors):
            btn = self.fg_color_buttons[i]
            # Clear any existing children (labels)
            btn.clean()
            # Add checkmark if this is the selected color
            if color_info["value"] == self.fg_color:
                label = lv.label(btn)
                label.set_text(lv.SYMBOL.OK)
                label.center()
                # Set contrasting color for the checkmark
                if color_info["value"] == 0x000000:  # Black background
                    label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
                else:
                    label.set_style_text_color(lv.color_hex(0x000000), 0)

        # Update background color buttons
        for i, color_info in enumerate(self.colors):
            btn = self.bg_color_buttons[i]
            # Clear any existing children (labels)
            btn.clean()
            # Add checkmark if this is the selected color
            if color_info["value"] == self.bg_color:
                label = lv.label(btn)
                label.set_text(lv.SYMBOL.OK)
                label.center()
                # Set contrasting color for the checkmark
                if color_info["value"] == 0x000000:  # Black background
                    label.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
                else:
                    label.set_style_text_color(lv.color_hex(0x000000), 0)


    def confirm_and_show_display(self, event):
        # Save the name from textarea
        self.name_text = self.name_ta.get_text()
        if not self.name_text or len(self.name_text.strip()) == 0:
            self.name_text = "Your Name"

        # Hide keyboard if visible
        self.hide_keyboard()

        # Update display screen with current settings
        self.update_display_screen()

        # Switch to display screen by hiding edit and showing display
        self.is_editing = False
        self.edit_screen.add_flag(lv.obj.FLAG.HIDDEN)
        self.display_screen.remove_flag(lv.obj.FLAG.HIDDEN)

        # Set focus to display screen so it receives key events
        focusgroup = lv.group_get_default()
        if focusgroup:
            mpos.ui.focus_direction.emulate_focus_obj(focusgroup, self.display_screen)

    def update_display_screen(self):
        # Set background color
        self.display_screen.set_style_bg_color(lv.color_hex(self.bg_color), 0)

        # Set text and color
        self.display_label.set_text(self.name_text)
        self.display_label.set_style_text_color(lv.color_hex(self.fg_color), 0)

        # Use the largest available font size
        self.display_label.set_style_text_font(lv.font_montserrat_30, 0)

        # Add generous letter spacing to make text appear larger and more spread out
        self.display_label.set_style_text_letter_space(10, 0)

        # Center the text
        self.display_label.set_width(lv.SIZE_CONTENT)
        self.display_label.center()

    def global_key_handler(self, event):
        # Handle Enter key press when on display screen
        if not self.is_editing:
            key = event.get_key()
            if key == lv.KEY.ENTER:
                self.show_edit_screen()

    def show_edit_screen(self, event=None):
        if not self.is_editing:
            self.is_editing = True
            # Hide keyboard if it's showing
            if self.keyboard and not self.keyboard.has_flag(lv.obj.FLAG.HIDDEN):
                self.hide_keyboard()
            # Update color indicators to show current selection
            self.update_color_indicators()
            # Switch back to edit screen by hiding display and showing edit
            self.display_screen.add_flag(lv.obj.FLAG.HIDDEN)
            self.edit_screen.remove_flag(lv.obj.FLAG.HIDDEN)

    def onStop(self, screen):
        # Clean up keyboard if visible
        if self.keyboard and not self.keyboard.has_flag(lv.obj.FLAG.HIDDEN):
            self.hide_keyboard()
