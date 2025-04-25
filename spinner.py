from turtle import *
import random
import colorsys
import math
import time
import os

# Try to import PIL for image support
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available. Custom image loading disabled.")

# Initial spinner state
state = {
    'turn': 0,
    'speed': 0,
    'angular_velocity': 0,
    'inertia': 0.995,  # Higher value = longer spin time
    'background_color': (1.0, 1.0, 1.0),
    'target_color': (1.0, 1.0, 1.0),
    'base_color_step': 0.01,
    'color_intensity': 0.5,  # Controls how vibrant background colors get
    'last_mouse_pos': None,
    'dragging': False,
    'drag_offset_x': 0,
    'drag_offset_y': 0,
    'drag_center_x': 0,
    'drag_center_y': 0,
    'last_update_time': time.time(),
    'last_angle': 0,
    'arm_count': 3,
    'arm_length': 100,
    'spinner_style': 'classic',  # 'classic', 'tri', 'gear', 'image'
    'effects_enabled': True,
    'handle_dragged': False,
    'spinner_radius': 150,
    'handle_radius': 40,
    'spinner_position': (0, 0),  # Center of spinner
    'handle_position': (0, 0),   # Position of draggable handle
    'transition_duration': 1.0,  # Background transition duration
    'background_init': True,     # Allow background changes
    'spinner_image': None,       # Store loaded spinner image
    'image_path': None,          # Path to spinner image
    'last_bg_update': 0,         # Last background update time
    'bg_update_interval': 0.05,  # Background update interval (seconds)
    'ui_elements': []            # Store UI element positions to avoid spinning them
}

# Global click handlers list
click_handlers = []

def load_spinner_image(path):
    """Load a custom spinner image if path exists."""
    if not PIL_AVAILABLE:
        print("PIL not available. Cannot load images.")
        return False
        
    try:
        if os.path.exists(path):
            # Load and create PhotoImage
            img = Image.open(path)
            # FIXED: Resize to maintain 1:1 aspect ratio with proper dimensions
            img = img.resize((int(state['spinner_radius']*2), int(state['spinner_radius']*2)), Image.Resampling.LANCZOS)
            # Convert to PhotoImage for turtle
            photo_img = ImageTk.PhotoImage(img)
            state['spinner_image'] = photo_img
            state['image_path'] = path
            state['spinner_style'] = 'image'
            return True
        else:
            print(f"Image not found: {path}")
            return False
    except Exception as e:
        print(f"Error loading image: {e}")
        return False
def draw_spinner():
    """Draw realistic spinner with arms connected to the center."""
    clear()
    
    # Draw UI elements first (so they don't rotate with spinner)
    if not state['dragging'] and not state['handle_dragged']:
        draw_speedometer()
        draw_text()
        draw_controls()
    
    # Set position based on spinner position
    penup()
    goto(state['spinner_position'])
    
    # Draw spinner based on selected style
    if state['spinner_style'] == 'image' and state['spinner_image']:
        draw_image_spinner()
    else:
        # Draw basic spinner with rotation
        setheading(state['turn'])  # Apply rotation to spinner
        
        # Draw central bearing
        penup()
        pendown()
        pencolor('black')
        fillcolor('gray')
        begin_fill()
        circle(state['handle_radius'])
        end_fill()
        
        # Add bearing details
        penup()
        pendown()
        fillcolor('darkgray')
        begin_fill()
        circle(10)
        end_fill()
        
        # Draw spinner arms based on selected style
        if state['spinner_style'] == 'classic':
            draw_classic_spinner()
        elif state['spinner_style'] == 'tri':
            draw_tri_spinner()
        elif state['spinner_style'] == 'gear':
            draw_gear_spinner()

    # Draw draggable handle (separate from spinner rotation)

    
    update()

def draw_image_spinner():
    """Draw spinner using loaded image with rotation."""
    if not state['spinner_image'] or not PIL_AVAILABLE:
        return
    
    # Calculate image position (centered on spinner position)
    # FIXED: Corrected the positioning calculation to center the image properly
    img_x = state['spinner_position'][0] - state['spinner_radius'] * 7.4442
    img_y = state['spinner_position'][1] - state['spinner_radius'] * -4.5
    
    try:
        # Get the original PIL image (we need to store this separately)
        if 'original_pil_image' not in state:
            # Get original image path
            image_path = state['image_path']
            # Open and store the original PIL image
            state['original_pil_image'] = Image.open(image_path)
            # Resize to appropriate size while maintaining 1:1 aspect ratio
            state['original_pil_image'] = state['original_pil_image'].resize(
                (int(state['spinner_radius']*2), int(state['spinner_radius']*2)), 
                Image.Resampling.LANCZOS
            )
        
        # Rotate the image based on current turn angle
        rotated_image = state['original_pil_image'].rotate(-state['turn'])  # Negative for clockwise rotation
        
        # Convert to PhotoImage
        rotated_photo = ImageTk.PhotoImage(rotated_image)
        
        # Store reference to prevent garbage collection
        state['current_rotated_image'] = rotated_photo
        
        # Get screen and canvas
        screen = getscreen()
        canvas = screen.getcanvas()
        
        # Clear previous images
        for item_id in canvas.find_withtag("spinner_img"):
            canvas.delete(item_id)
        
        # FIXED: Updated image placement to properly center it
        canvas.create_image(
            img_x + screen.window_width() // 2,
            screen.window_height() // 2 - img_y,
            image=state['current_rotated_image'],
            tags=("spinner_img",),
            anchor="nw"
        )
        
    except Exception as e:
        print(f"Error in image rotation: {e}")
        # Fallback to original method if something goes wrong
        screen = getscreen()
        canvas = screen.getcanvas()
        for item_id in canvas.find_withtag("spinner_img"):
            canvas.delete(item_id)
            
        canvas.create_image(
            img_x + screen.window_width() // 2,
            screen.window_height() // 2 - img_y,
            image=state['spinner_image'],
            tags=("spinner_img",),
            anchor="nw"
        )

def draw_handle():
    """Draw draggable handle element."""
    # Save current position and heading
    current_pos = position()
    current_heading = heading()
    
    # Go to handle position
    penup()
    goto(state['handle_position'])
    pendown()
    

    
    # Draw grip lines for visual effect
    pencolor('black')
    for i in range(3):
        penup()
        goto(state['handle_position'][0], state['handle_position'][1] + i * 7 - 7)
        pendown()
        forward(20)
    
    # Restore position and heading
    penup()
    goto(current_pos)
    setheading(current_heading)
    pendown()

def draw_classic_spinner():
    """Draw a classic 3-arm spinner with improved graphics."""
    arm_count = state['arm_count']
    arm_length = state['arm_length']
    

    
    # Draw arms with circles
    for i in range(arm_count):
        angle = 360 / arm_count * i
        draw_arm(angle, arm_length)

def draw_tri_spinner():
    """Draw a triangular spinner with improved graphics."""
    arm_length = state['arm_length']
    
    # Draw triangle
    penup()
    pendown()
    pencolor('black')
    fillcolor('#50C878')  # Emerald green
    begin_fill()
    
    for i in range(3):
        setheading(state['turn'] + 120 * i)
        forward(arm_length)
        left(120)
        forward(arm_length)
        right(180)
    
    end_fill()
    
    # Draw circles at vertices with metallic look
    for angle in [0, 120, 240]:
        penup()
        goto(state['spinner_position'])
        setheading(state['turn'] + angle)
        forward(arm_length)
        pendown()
        fillcolor('#D3D3D3')  # Light gray
        begin_fill()
        circle(15)
        end_fill()
        
        # Add metallic detail
        fillcolor('#A0A0A0')  # Darker gray for 3D effect
        begin_fill() 
        circle(8)
        end_fill()

def draw_gear_spinner():
    """Draw a gear-style spinner with improved graphics."""
    arm_length = state['arm_length']
    tooth_count = 12
    
    penup()
    goto(state['spinner_position'])
    pendown()
    
    # Draw main gear body with metallic gradient
    fillcolor('#B8B8B8')  # Lighter metallic
    begin_fill()
    circle(arm_length * 0.7)
    end_fill()
    
    # Inner detail
    fillcolor('#969696')  # Darker metallic for 3D effect
    begin_fill()
    circle(arm_length * 0.5)
    end_fill()
    
    # Central hub
    fillcolor('#787878')  # Even darker for depth
    begin_fill()
    circle(arm_length * 0.3)
    end_fill()
    
    # Draw gear teeth with 3D appearance
    for i in range(tooth_count):
        angle = 360 / tooth_count * i
        penup()
        goto(state['spinner_position'])
        setheading(state['turn'] + angle)
        forward(arm_length * 0.7)
        pendown()
        
        # Save position to return to
        tooth_base = position()
        
        # Draw 3D-looking tooth
        fillcolor('#D3D3D3')  # Light gray for tooth
        begin_fill()
        for _ in range(2):
            forward(20)
            right(90)
            forward(10)
            right(90)
        end_fill()
        
        # Return to tooth base
        penup()
        goto(tooth_base)
        pendown()

def draw_arm(angle, length):
    """Draw one spinner arm with connected line and outer circle - improved graphics."""
    # Save starting position (center)
    center_pos = position()
    
    # Draw line from center to arm
    penup()
    setheading(angle + state['turn'])
    pendown()
    pencolor('black')
    pensize(4)
    forward(length)
    
    # Save arm position
    arm_pos = position()

    # Draw outer circle at the end of arm with gradient for 3D effect
    fillcolor('#5A5A5A')  # Dark gray base
    begin_fill()
    circle(30)
    end_fill()
    
    # Add highlight circle for 3D effect
    fillcolor('#D3D3D3')  # Light gray highlight
    begin_fill()
    circle(20)
    end_fill()
    
    # Add "weight" circle in middle
    fillcolor('#B8B8B8')  # Medium gray
    begin_fill()
    circle(10)
    end_fill()
    
    # Outer decorative ring
    penup()
    circle(30, 180)
    pendown()
    pencolor('black')
    pensize(2)
    circle(30, 360)

def draw_speedometer():
    """Visual arc based on speed."""
    x, y = state['spinner_position']
    penup()
    goto(x, y - 180)
    setheading(0)
    pendown()
    speed_ratio = min(abs(state['angular_velocity']) / 20, 1)
    arc_extent = 180 * speed_ratio
    
    # Gradient based on speed
    if speed_ratio < 0.3:
        pencolor('blue')
    elif speed_ratio < 0.7:
        pencolor('green')
    else:
        pencolor('red')
        
    pensize(5)
    circle(180, arc_extent)
    
    # Store speedometer position in UI elements
    state['ui_elements'].append(('speedometer', (x, y - 180)))

def draw_text():
    """Display spinner values with improved layout."""
    text_x = -230
    text_y = 180
    text_spacing = 22  # Increased spacing
    
    penup()
    goto(text_x, text_y)
    color('black')
    
    # Display info with better formatting
    speed_text = f"Speed: {abs(state['angular_velocity']):.2f}"
    write(speed_text, font=("Arial", 12, "bold"))
    
    goto(text_x, text_y - text_spacing)
    write(f"Direction: {'Forward' if state['angular_velocity'] >= 0 else 'Backward'}", 
          font=("Arial", 12, "normal"))
    
    goto(text_x, text_y - 2*text_spacing)
    write(f"Style: {state['spinner_style'].capitalize()}", font=("Arial", 12, "normal"))
    
    goto(text_x, text_y - 3*text_spacing)
    write(f"Arms: {state['arm_count']}", font=("Arial", 12, "normal"))
    
    goto(text_x, text_y - 4*text_spacing)
    write(f"Effects: {'On' if state['effects_enabled'] else 'Off'}", font=("Arial", 12, "normal"))
    
    goto(text_x, text_y - 5*text_spacing)
    write("Drag the red handle or the spinner!", font=("Arial", 12, "bold"))
    
    # Store text positions in UI elements
    for i in range(6):
        state['ui_elements'].append(('text', (text_x, text_y - i*text_spacing)))

def draw_controls():
    """Draw clickable control buttons with improved styling."""
    # Clear UI elements list for buttons
    buttons = [b for b in state['ui_elements'] if b[0] != 'button']
    state['ui_elements'] = buttons
    

    

def draw_button(x, y, w, h, text, command=None):
    """Draw a clickable button with improved styling."""
    # Using w and h instead of width and height to avoid name conflicts
    penup()
    goto(x, y)
    pendown()
    
    # Store button position in UI elements
    state['ui_elements'].append(('button', (x, y, w, h)))
    
    # Button base with gradient effect
    pencolor('black')
    fillcolor('#E0E0E0')  # Light gray for button
    begin_fill()
    for _ in range(2):
        forward(w)
        left(90)
        forward(h)
        left(90)
    end_fill()
    
    # Button border
    pensize(2)
    for _ in range(2):
        forward(w)
        left(90)
        forward(h)
        left(90)
    
    # 3D effect - top highlight
    penup()
    goto(x + 2, y + h - 2)
    pendown()
    pencolor('#FFFFFF')  # White highlight
    goto(x + w - 2, y + h - 2)
    
    # 3D effect - left highlight
    goto(x + 2, y + 2)
    
    # 3D effect - bottom shadow
    pencolor('#A0A0A0')  # Dark gray shadow
    goto(x + w - 2, y + 2)
    goto(x + w - 2, y + h - 2)
    
    # Add button text
    penup()
    goto(x + w/2 - 5 * len(text), y + h/2 - 7)
    pencolor('black')
    write(text, font=("Arial", 12, "normal"))
    
    # Register clickable area
    if command:
        onclick_area(x, y, w, h, command)

def onclick_area(x, y, w, h, command):
    """Register a clickable area."""
    def check_click(x_click, y_click):
        if x <= x_click <= x + w and y <= y_click <= y + h:
            command()
    
    # Add to global click handlers list
    global click_handlers
    click_handlers.append(check_click)

def animate():
    """Handle animation frame with improved physics."""
    # Calculate delta time for smooth animation
    current_time = time.time()
    dt = min(current_time - state['last_update_time'], 0.1)  # Cap dt to avoid large jumps
    state['last_update_time'] = current_time
    
    # Apply physics with time delta
    if abs(state['angular_velocity']) > 0.001:  # Lower threshold to keep spinning longer
        # Apply rotation based on current speed
        state['turn'] += state['angular_velocity'] * dt * 60  # Scale by 60 to maintain similar speed
        
        # Apply inertia with more realistic physics
        state['angular_velocity'] *= pow(state['inertia'], dt * 60)  # Smoother decay
        
        # More aggressive background color change based on speed
        if state['effects_enabled'] and state['background_init']:
            # Only update background at intervals to improve performance
            if current_time - state['last_bg_update'] >= state['bg_update_interval']:
                transition_background()
                state['last_bg_update'] = current_time
    else:
        state['angular_velocity'] = 0
    
    # Handle dragging logic
    if state['dragging']:
        handle_spinner_drag()
    elif state['handle_dragged']:
        handle_handle_drag()

    draw_spinner()
    ontimer(animate, 16)  # ~60 FPS

def load_image():
    """Prompt for image path and load it."""
    if not PIL_AVAILABLE:
        print("PIL not available. Cannot load images.")
        return
        
    screen = getscreen()
    path = screen.textinput("Load Image", "Enter path to spinner image:")
    if path:
        if load_spinner_image(path):
            print(f"Loaded image: {path}")
        else:
            print(f"Failed to load image: {path}")

def flick():
    """Flick the spinner with random direction and high speed."""
    direction = 1 if random.random() > 0.5 else -1
    state['angular_velocity'] = 20 * direction  # Increased speed

def change_style():
    """Cycle through spinner styles."""
    styles = ['classic', 'tri', 'gear']
    
    # Add image style only if image is loaded
    if state['spinner_image']:
        styles.append('image')
        
    # Find current style index
    try:
        current_index = styles.index(state['spinner_style'])
    except ValueError:
        current_index = 0
        
    # Set next style
    state['spinner_style'] = styles[(current_index + 1) % len(styles)]

def increase_arms():
    """Increase number of arms (max 6)."""
    state['arm_count'] = min(6, state['arm_count'] + 1)

def decrease_arms():
    """Decrease number of arms (min 2)."""
    state['arm_count'] = max(2, state['arm_count'] - 1)

def toggle_effects():
    """Toggle color effects on/off."""
    state['effects_enabled'] = not state['effects_enabled']
    if not state['effects_enabled']:
        # Reset to white background when effects are disabled
        state['background_color'] = (1.0, 1.0, 1.0)
        bgcolor(state['background_color'])

def lerp_colors(color1, color2, t):
    """Linear interpolation between two colors."""
    r = color1[0] + (color2[0] - color1[0]) * t
    g = color1[1] + (color2[1] - color1[1]) * t
    b = color1[2] + (color2[2] - color1[2]) * t
    return (r, g, b)

def transition_background():
    """Change background color gradually based on spinner speed - improved."""
    # Increase step based on speed - more dynamic
    speed_factor = min(abs(state['angular_velocity']) / 15, 1)  # More sensitive to speed
    step = state['base_color_step'] * speed_factor * 5  # Faster transitions
    
    current = state['background_color']
    target = state['target_color']
    new_color = lerp_colors(current, target, step)
    state['background_color'] = new_color
    bgcolor(new_color)

    # Pick new target if close enough
    if all(abs(a - b) < 0.01 for a, b in zip(new_color, target)):
        # Generate vibrant colors based on speed
        intensity = min(0.3 + speed_factor * 0.7, 1.0)  # Higher speed = more vibrant
        state['target_color'] = hsv_color(intensity)

def hsv_color(intensity=0.8):
    """Return smooth random RGB from HSV with adjustable saturation."""
    h = random.random()
    r, g, b = colorsys.hsv_to_rgb(h, intensity, 1.0)
    return (r, g, b)

def reset():
    """Reset to original state."""
    state.update({
        'turn': 0,
        'speed': 0,
        'angular_velocity': 0,
        'inertia': 0.995,
        'background_color': (1.0, 1.0, 1.0),
        'target_color': (1.0, 1.0, 1.0),
        'arm_count': 3,
        'spinner_style': 'classic',
        'effects_enabled': True,
        'spinner_position': (0, 0),
        'handle_position': (0, 0),
        'background_init': True
    })
    bgcolor(state['background_color'])

def resize_me():
    """Initialize positions."""
    state['spinner_position'] = (0, 0)
    state['handle_position'] = (0, 0)

# Mouse handling functions
def handle_mouse_click(x, y, button_state):
    """Handle mouse clicks and releases with improved detection."""
    if button_state == 1:  # Mouse down
        # Check if clicking on the handle
        handle_x, handle_y = state['handle_position']
        distance_to_handle = math.sqrt((x - handle_x)**2 + (y - handle_y)**2)
        
        # Check if clicking on the spinner center
        spinner_x, spinner_y = state['spinner_position']
        distance_to_spinner = math.sqrt((x - spinner_x)**2 + (y - spinner_y)**2)
        
        if distance_to_handle <= state['handle_radius'] * 1.5:
            # Dragging the handle
            state['handle_dragged'] = True
            state['drag_offset_x'] = x - handle_x
            state['drag_offset_y'] = y - handle_y
            
        elif distance_to_spinner <= state['spinner_radius']:
            # Dragging the spinner itself
            state['dragging'] = True
            state['last_mouse_pos'] = (x, y)
            state['last_angle'] = math.degrees(math.atan2(y - spinner_y, x - spinner_x))
            on_drag_start()
            
    else:  # Mouse up
        if state['dragging'] or state['handle_dragged']:
            on_drag_stop()
            
        state['dragging'] = False
        state['handle_dragged'] = False
        
        # Check for button clicks when releasing
        for handler in click_handlers:
            handler(x, y)

def handle_spinner_drag():
    """Update spinner physics based on mouse movement - improved rotation."""
    if not state['last_mouse_pos']:
        return
        
    # Get spinner center
    spinner_x, spinner_y = state['spinner_position']
    
    # Calculate rotation from last position to current mouse position
    x, y = state['last_mouse_pos']
    
    # Calculate the rotation needed
    screen = getscreen()
    new_x, new_y = screen.getcanvas().winfo_pointerxy()
    win_x, win_y = screen.getcanvas().winfo_rootx(), screen.getcanvas().winfo_rooty()
    
    # Adjust coordinates relative to center of canvas
    new_x = new_x - win_x - screen.window_width() // 2
    new_y = win_y + screen.window_height() // 2 - new_y
    
    # Skip if mouse hasn't moved significantly 
    if abs(new_x - x) < 1 and abs(new_y - y) < 1:
        return
    
    # Calculate angles from center
    new_angle = math.degrees(math.atan2(new_y - spinner_y, new_x - spinner_x))
    
    # Calculate angular difference
    angle_diff = new_angle - state['last_angle']
    
    # Adjust for angle wrapping
    if angle_diff > 180:
        angle_diff -= 360
    elif angle_diff < -180:
        angle_diff += 360
    
    # Set spinner speed based on the angular change
    # Increased scale factor for more responsive spinning
    scale_factor = 1.5
    state['angular_velocity'] = angle_diff * scale_factor
    
    # Update spinner rotation directly to follow mouse
    state['turn'] += angle_diff
    
    # Update last values
    state['last_angle'] = new_angle
    state['last_mouse_pos'] = (new_x, new_y)

def handle_handle_drag():
    """Handle dragging of the handle element with fixed center offset."""
    # Get the current mouse position
    screen = getscreen()
    mouse_x, mouse_y = screen.getcanvas().winfo_pointerxy()
    win_x, win_y = screen.getcanvas().winfo_rootx(), screen.getcanvas().winfo_rooty()
    
    # Adjust coordinates relative to center of canvas
    mouse_x = mouse_x - win_x - screen.window_width() // 2
    mouse_y = win_y + screen.window_height() // 2 - mouse_y
    
    # Update handle position, accounting for drag offset
    new_x = mouse_x - state['drag_offset_x']
    new_y = mouse_y - state['drag_offset_y']
    
    # Update handle position
    state['handle_position'] = (new_x, new_y)
    
    # Update spinner position to match handle
    state['spinner_position'] = (new_x, new_y)

def on_drag_start():
    """Called when dragging starts."""
    # Enable background animation
    state['background_init'] = True

def on_drag_stop():
    """Called when dragging ends."""
    # Keep momentum from dragging
    pass

def increase_speed():
    """Increase spinner speed."""
    state['angular_velocity'] += 2  # Increased from 1

def decrease_speed():
    """Decrease spinner speed."""
    state['angular_velocity'] -= 2  # Increased from 1

# Setup
def init():
    setup(2000, 2000, 0, 0)  # Increased window size
    title("Advanced Fidget Spinner")
    hideturtle()
    tracer(False)
    pensize(3)
    bgcolor(state['background_color'])
    
    # Auto-load spinner.png from current directory
    if PIL_AVAILABLE:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        spinner_path = os.path.join(current_dir, "spinner.png")
        if os.path.exists(spinner_path):
            load_spinner_image(spinner_path)
            print(f"Loaded spinner image: {spinner_path}")
        else:
            print(f"No spinner.png found in {current_dir}")
    
    # Controls
    onkey(flick, 'space')
    onkey(increase_speed, 'Up')
    onkey(decrease_speed, 'Down')
    onkey(change_style, 's')
    onkey(toggle_effects, 'e')
    onkey(increase_arms, 'a')
    onkey(decrease_arms, 'd')
    onkey(reset, 'r')
    
    # Mouse handling
    screen = getscreen()
    
    # Create mouse press and release handlers
    def on_click(x, y):
        handle_mouse_click(x, y, 1)  # Mouse down
    
    def on_release(x, y):
        handle_mouse_click(x, y, 0)  # Mouse up
    
    # Use onscreenclick for mouse down events
    screen.onscreenclick(on_click, 1)  # Button 1 press
    
    # Use binding for mouse up events
    screen.getcanvas().bind("<ButtonRelease-1>", lambda event: on_release(
        screen.cv.canvasx(event.x) - screen.cv.winfo_width() // 2,
        screen.cv.winfo_height() // 2 - screen.cv.canvasy(event.y)
    ))
    
    # Implement initialize positions
    resize_me()
    
    # Ask for spinner image when starting
    if PIL_AVAILABLE:
        pass
    
    # Instructions
    print("=== ENHANCED FIDGET SPINNER ===")
    print("CONTROLS:")
    print("- DRAG the RED HANDLE to move the spinner around")
    print("- DRAG the SPINNER itself to rotate it")
    print("- SPACE: Flick spinner")
    # Instructions
    print("=== ENHANCED FIDGET SPINNER ===")
    print("CONTROLS:")
    print("- DRAG the RED HANDLE to move the spinner around")
    print("- DRAG the SPINNER itself to rotate it")
    print("- SPACE: Flick spinner")
    print("- UP/DOWN: Increase/decrease speed")
    print("- S: Change spinner style")
    print("- A/D: Add/remove arms")
    print("- E: Toggle color effects")
    print("- R: Reset spinner")
    print("- Click buttons to use controls")
    
    listen()
    state['last_update_time'] = time.time()
    animate()



# Start the program
if __name__ == "__main__":
    init()
    done()