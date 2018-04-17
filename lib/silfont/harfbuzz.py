#!/usr/bin/python
'Harfbuzz support for fonttools'

import gi
gi.require_version('HarfBuzz', '0.0')
from gi.repository import HarfBuzz as hb
from gi.repository import GLib

class Glyph(object):
    def __init__(self, gid, **kw):
        self.gid = gid
        for k,v in kw.items():
            setattr(self, k, v)

    def __repr__(self):
        return "[{gid}@({offset[0]},{offset[1]})+({advance[0]},{advance[1]})]".format(**self.__dict__)

def shape_text(f, text, features = [], lang=None, dir="", script="", shapers=""):
    fontfile = f.reader.file
    fontfile.seek(0, 0)
    fontdata = fontfile.read()
    blob = hb.glib_blob_create(GLib.Bytes.new(fontdata))
    face = hb.face_create(blob, 0)
    del blob
    font = hb.font_create(face)
    upem = hb.face_get_upem(face)
    del face
    hb.font_set_scale(font, upem, upem)
    hb.ot_font_set_funcs(font)

    buf = hb.buffer_create()
    t = text.encode('utf-8')
    hb.buffer_add_utf8(buf, t, 0, -1)
    hb.buffer_guess_segment_properties(buf)
    if dir:
        hb.buffer_set_direction(buf, hb.direction_from_string(dir))
    if script:
        hb.buffer_set_script(buf, hb.script_from_string(script))
    if lang:
        hb.buffer_set_language(buf, hb.language_from_string(lang))
    
    feats = []
    if len(features):
        for feat_string in features:
            if hb.feature_from_string(feat_string, -1, aFeats):
                feats.append(aFeats)
    if shapers:
        hb.shape_full(font, buf, feats, shapers)
    else:
        hb.shape(font, buf, feats)

    num_glyphs = hb.buffer_get_length(buf)
    info = hb.buffer_get_glyph_infos(buf)
    pos = hb.buffer_get_glyph_positions(buf)

    glyphs = []
    for i in range(num_glyphs):
        glyphs.append(Glyph(info[i].codepoint, cluster = info[i].cluster,
                        offset = (pos[i].x_offset, pos[i].y_offset),
                        advance = (pos[i].x_advance, pos[i].y_advance),
                        flags = info[i].mask))
    return glyphs

if __name__ == '__main__':
    import sys
    from fontTools.ttLib import TTFont
    font = sys.argv[1]
    text = sys.argv[2]
    f = TTFont(font)
    glyphs = shape_text(f, text)
    print glyphs
