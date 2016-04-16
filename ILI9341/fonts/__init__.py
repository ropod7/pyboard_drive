# -*- coding: utf-8 -*-

__all__ = []

def importing(font):
    if font == 'Arial_14':
        from fonts.arial_14 import Arial_14 as font
    elif font == 'Vera_14':
        from fonts.vera_14 import Vera_14 as font
    elif font == 'VeraMono_14':
        from fonts.veram_14 import VeraMono_14 as font
    elif font == 'Vera_23':
        from fonts.vera_23 import Vera_23 as font
    elif font == 'Heydings_23':
        from fonts.heyd_23 import Heydings_23 as font
    else:
        raise ImportError('wrong font name: ' + font)
    return font