# Avaliable fonts:
#'VeraMono_10',
#'Vera_10',
#'Arial_14',
#'Vera_14',
#'VeraMono_14',
#'Pitch_14',
#'Pitch_22',
#'Vera_23',
#'VeraMono_23',
#'Heydings_23',
#'Entypo_14',
#'Entypo_23',

__all__ = []

def importing(font):
    if font == 'VeraMono_10':
        from fonts.veram_10 import VeraMono_10 as font
    elif font == 'Vera_10':
        from fonts.vera_10 import Vera_10 as font
    elif font == 'Arial_14':
        from fonts.arial_14 import Arial_14 as font
    elif font == 'Vera_14':
        from fonts.vera_14 import Vera_14 as font
    elif font == 'VeraMono_14':
        from fonts.veram_14 import VeraMono_14 as font
    elif font == 'Pitch_14':
        from fonts.pitch_14 import Pitch_14 as font
    elif font == 'Pitch_22':
        from fonts.pitch_22 import Pitch_22 as font
    elif font == 'Vera_23':
        from fonts.vera_23 import Vera_23 as font
    elif font == 'VeraMono_23':
        from fonts.veram_23 import VeraMono_23 as font
    elif font == 'Heydings_23':
        from fonts.heyd_23 import Heydings_23 as font
    elif font == 'Entypo_14':
        from fonts.etypo_14 import Entypo_14 as font
    elif font == 'Entypo_23':
        from fonts.etypo_23 import Entypo_23 as font
    else:
        raise ImportError('wrong font name: ' + font)
    return font