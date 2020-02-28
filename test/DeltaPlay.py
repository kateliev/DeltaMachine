#FLM: TR: Delta Playground
# ----------------------------------------
# (C) Vassil Kateliev, 2019 (http://www.kateliev.com)
# (C) Karandash Type Foundry (http://www.karandash.eu)
#-----------------------------------------
# www.typerig.com

# No warranties. By using this you agree
# that you use it at your own risk!

# - Dependencies -----------------
import os, json
from math import radians

import fontlab as fl6
import fontgate as fgt

from typerig.proxy import pFont
from typerig.glyph import eGlyph
from typerig.node import eNode
from typerig.gui import getProcessGlyphs
from typerig.brain import coordArray, linInterp, ratfrac

from lib import transform

# - Play --------------------------------
wGlyph = eGlyph()

# - Axis
a = wGlyph._getCoordArray('R')
b = wGlyph._getCoordArray('B')

# - Compensation
scmp = (0.,0.)
angle = 0.

# - Stems
sw_dx = [20, 100]
sw_dy = [15, 85]

curr_sw_dx = 100
curr_sw_dy = 15

# - Stem values
sw_dx0, sw_dx1 = sorted(sw_dx)
sw_dy0, sw_dy1 = sorted(sw_dy)
st_arr = [sw_dx0, sw_dx1, sw_dy0, sw_dy1]

# - Interpolation times
tx = transform.timer(curr_sw_dx, sw_dx0, sw_dx1, True)
ty = transform.timer(curr_sw_dy, sw_dy0, sw_dy1, True)

# - Scaling
sx = 200./420 	# scale X
sy = 71.42/100  # scale Y

dx, dy = 0.0, 0.0 # shift X, Y

joined_array = zip(a.asPairs(), b.asPairs())
sx, sy = transform.adjuster(joined_array, (200./420, sy), (tx, ty), st_arr)
mm_scaler = lambda sx, sy, tx, ty : transform.adaptive_scale_array(joined_array, (sx, sy), (dx, dy), (tx, ty), (scmp[0], scmp[1]), angle, st_arr)

wGlyph._setCoordArray(mm_scaler(sx , sy, tx, ty), layer='T')
wGlyph.updateObject(wGlyph.fl, 'tx: %s, ty: %s' %(tx,ty))
			


