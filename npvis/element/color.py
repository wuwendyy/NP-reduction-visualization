# RGB colors
LIGHTBLUE = (173, 216, 230)
LIGHTPINK = (255, 192, 203)
LIGHTGREY = (211, 211, 211)

# helper function to change opacity by rgb
def lighten_rgb(rgb, opacity, gamma=2.2):
    """
    Lightens an RGB color by blending it with white using gamma correction.

    Parameters:
    - rgb: tuple of 3 ints (0–255), the original RGB color
    - opacity: float between 0 and 1, how much white to blend in
    - gamma: float, gamma value (default 2.2)

    Returns:
    - lightened_rgb: tuple of 3 ints (0–255), the lightened RGB color
    """
    result = []
    for c in rgb:
        linear_c = pow(c / 255.0, gamma)
        linear_white = pow(1.0, gamma)  # White component is always 1.0
        blended_linear = (linear_c * (1 - opacity)) + (linear_white * opacity)
        corrected = pow(blended_linear, 1 / gamma)
        result.append(int(round(corrected * 255)))
    return tuple(result)