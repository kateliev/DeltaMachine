# MODULE: Transform Core | DeltaMachine | TypeRig
# ----------------------------------------
# (C) Vassil Kateliev, 2018  (http://www.kateliev.com)
# (C) Karandash Type Foundry (http://www.karandash.eu)
#-----------------------------------------
# www.typerig.com

# NOTE:
# A Pure python implementation

# No warranties. By using this you agree
# that you use it at your own risk!

__version__ = '0.0.2'

# - Dependencies ------------------------
from math import radians

# - Functions ---------------------------
def compensator(sf, cf, st0, st1):
	b = float(st1)/st0
	try:
		q = float(sf**(cf - 1.) - b)/(1. - b)
	except ZeroDivisionError:
		q = 0
	return q

def lerp(t0, t1, t):
	return (t1 - t0)*t + t0

# -- Adaptive scaling --------------------------------------------
# Based on: A Multiple Master based method for scaling glyphs without changing the stroke characteristics
# By: Tim Ahrens 
# URL: https://remix-tools.com/pdf/Tim_Ahrens_MM_method.pdf

def adaptive_scale(v, s, d, t, c, i, st):
	'''Perform adaptive scaling by keeping the stem/stroke weights
	Args:
		v(t0, t1) -> tuple((float, float), (float, float)) : Joined coordinates for both weights
		s(sx, sy) -> tuple((float, float) : Scale factors (X, Y)
		d(dx, dy) -> tuple((float, float) : Translate values (X, Y) 
		t(tx, ty) -> tuple((float, float) : Interpolation times (anisotropic X, Y) 
		c(cx, cy) -> tuple((float, float) : Compensation factor 0.0 (no compensation) to 1.0 (full compensation) (X,Y)
		i -> (radians) : Angle of sharing (for italic designs)  
		st(stx0, stx1, sty0, sty1) -> tuple((float, float, float, float) : Stems widths for weights t0, t1

	Returns:
		tuple(float, float): Transformed coordinate data
	'''
	
	# - Init
	v0, v1 = v 						# Coordinates (x0, y0) (x1, y1)
	sx, sy = s 						# Scale X, Y
	dx, dy = d 						# Translate delta X, Y
	tx, ty = t 						# Interpolate time tx, ty
	cx, cy = c 						# Compensation x, y
	stx0, stx1, sty0, sty1 = st 	# Stems values

	# - Calculate
	vtx = lerp(v0[0], v1[0], tx)
	vty = lerp(v0[1], v1[1], ty)
	
	cstx = lerp(stx0, stx1, tx)
	csty = lerp(sty0, sty1, ty)

	qx = compensator(sx, cx, cstx, stx1)
	qy = compensator(sy, cy, csty, sty1)

	ry = sy*(qy*vty + (1 - qy)*v1[1]) + dy
	rx = sx*(qx*(vtx - vty*i) + (1 - qx)*(v1[0] - v1[1]*i)) + ry*i + dx

	return (rx, ry)


def adaptive_scale_array(a, s, d, t, c, i, st):
	'''Perform adaptive scaling by keeping the stem/stroke weights
	Args:
		a(t0, t1) -> list(tuple(float, float), (float, float)) : Joined coordinate arrays for both weights
		s(sx, sy) -> tuple((float, float) : Scale factors (X, Y)
		d(dx, dy) -> tuple((float, float) : Translate values (X, Y) 
		t(tx, ty) -> tuple((float, float) : Interpolation times (anisotropic X, Y) 
		c(cx, cy) -> tuple((float, float) : Compensation factor 0.0 (no compensation) to 1.0 (full compensation) (X,Y)
		i -> (radians) : Angle of sharing (for italic designs)  
		st(stx0, stx1, sty0, sty1) -> tuple((float, float, float, float) : Stems widths for weights t0, t1

	Returns:
		list(tuple(float, float)): Transformed coordinate data
	'''
	return list(map(lambda a_i: adaptive_scale(a_i, s, d, t, c, i, st), a))