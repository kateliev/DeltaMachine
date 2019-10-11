# MODULE: Transform Core (NumPy) | DeltaMachine | TypeRig
# ----------------------------------------
# (C) Vassil Kateliev, 2018  (http://www.kateliev.com)
# (C) Karandash Type Foundry (http://www.karandash.eu)
#-----------------------------------------
# www.typerig.com

# NOTE:
# A SciPy, NumPy dependent module for various math and science related functions.

# No warranties. By using this you agree
# that you use it at your own risk!

__version__ = '0.2.5'

# - Dependencies -----------------
#import math
#import numpy as np
#import scipy as sp

# - Functions ------------------------------------------------
# -- Interpolation -------------------------------------------
def lerp1d(t0, t1, t):
	'''1D Interpolation using Numpy (Matrix version)
	Args:
		t0, t1 (list(float)): Data to be interpolated. Could contain nested lists [[X coords], [Y coords]]
		t (float) : Interpolation time
	Returns:
		nparray: Interpolated data
	'''
	from numpy import array, asarray, matmul
	tm = array([t, -t, 1.0 ])
	ta = asarray([t1, t0, t0])
	return matmul(ta.T, tm)

def axis_lerp1d(axisDict):
	'''1D Interpolation using SciPy. Takes multiple Axis instances specified by axis dict
	Args:
		data (dict(location(int): typerig.brain.coordArray)): A data container of all coordinate values to be interpolated.
	Returns:
		function(time): A one dimensional interpolation function of time. 
	'''
	from scipy.interpolate import interp1d
	from typerig.brain import coordArray

	data = zip(*[axisDict[key].flatten() for key in sorted(axisDict.keys())])

	lerp = interp1d(sorted(axisDict.keys()), data, bounds_error=False, fill_value='extrapolate')
	return lambda time: coordArray(lerp(time))

# -- Affine transformations --------------------------------------
def affine_transform(coordlist, tmatrix):
	'''Perform affine transformation according to given transformation matrix
	Args:
		coordlist (list(float)): Coordinates data. Could contain nested lists [[X coords], [Y coords]]
		tmatrix (list/nparray) : A 3x2 Affine Transformation matrix
	Returns:
		(nparray): Transformed coordinate data
	'''
	from numpy import array, asarray, matmul
	return matmul(asarray(coordlist).T, asarray(tmatrix))

def tmatrix_translate(dx, dy):
	from numpy import asarray
	return asarray([1., 0., dx, 0., 1., dy, 0., 0., 1. ]).reshape((3,3))

def tmatrix_scale(sx, sy, dx, dy):
	from numpy import asarray
	return asarray([sx, 0., dx, 0., sy, dy, 0., 0., 1. ]).reshape((3,3))

def tmatrix_shear(sxa, sya, dx, dy):
	from numpy import asarray
	from math import tan
	return asarray([1., tan(sxa), dx, tan(sya), 1., dy, 0., 0., 1. ]).reshape((3,3))

def tmatrix_rotate(rad, dx, dy):
	from numpy import asarray
	from math import sin, cos
	return asarray([cos(rad), sin(rad), dx, -sin(rad), cos(rad), dy, 0., 0., 1. ]).reshape((3,3))

# -- Adaptive scaling --------------------------------------------
# Based on: A Multiple Master based method for scaling glyphs without changing the stroke characteristics
# By: Tim Ahrens 
# URL: https://remix-tools.com/pdf/Tim_Ahrens_MM_method.pdf

def adaptive_scale_array(t0, t1, sx, sy, dx, dy, tx, ty, cx, cy, rad, st):
	'''Perform adaptive scaling by keeping the stem/stroke weights
	Args:
		t0, t1 (list((float))) : Coordinate arrays for both weights
		sx, sy (float) : Scale factors (X, Y)
		dx, dy (float) : Translate values (X, Y) 
		tx, ty (float) : Interpolation times (anisotropic X, Y) 
		cx, cy (float) : Compensation factor 0.0 (no compensation) to 1.0 (full compensation) (X,Y)
		rad (radians) : Angle of sharing (for italic designs)  
		st0, st1 (float) : Stems widths for weights t0, t1

	Returns:
		(nparray): Transformed coordinate data
	'''
	# !NOTE: Initial reimplementation from original Fortran 95 code by Kateliev

	from numpy import array, asarray, matmul, tan, ones, append

	def compensator(sf, cf, st0, st1):
		b = float(st1)/st0
		try:
			q = float(sf**(cf - 1.) - b)/(1. - b)
		except ZeroDivisionError:
			q = 0
		return q
	
	# - Init
	st0, st1, st2, st3 = st
	
	# -- Pure interpolation
	ctx = lerp1d(t0[0], t1[0], tx)
	cty = lerp1d(t0[1], t1[1], ty)
	cst = (st1 - st0)*tx + st0
	cst1 = (st3 - st2)*ty + st2

	# - Build compensation matrices
	# -- Compensation coefficients
	qx = compensator(sx, cx, cst, st1)
	qy = compensator(sy, cy, cst1, st3)

	qxm = asarray([qx, 1., -qx]).T
	qym = asarray([qy, 1., -qy]).T

	mty = asarray([cty, t1[1], t1[1]])

	if rad == 0.:
		# -- X coordinates with no italic angle
		mtx = asarray([ctx, t1[0], t1[0]])

		# -- Compensate
		cxy = asarray([matmul(mtx.T, qxm), matmul(mty.T, qym)])
		txy =  ones((cxy.shape[0] + 1, cxy.shape[1]))
		txy[0], txy[1] = cxy[0], cxy[1]
		
		# -- Affine Scale
		rxy = affine_transform(txy, tmatrix_scale(sx, sy, dx, dy))

		return rxy[:,:2]

	else:
		# -- X coordinates with italic angle (unslant)
		mtx = asarray([ctx - cty * tan(rad), asarray(t1[0]) - asarray(t1[1]) * tan(rad), asarray(t1[0]) - asarray(t1[1]) * tan(rad)])

		# -- Compensate with italic angle
		cxy = asarray([matmul(mtx.T, qxm), matmul(mty.T, qym)])
		txy =  ones((cxy.shape[0] + 1, cxy.shape[1]))
		txy[0], txy[1] = cxy[0], cxy[1]
		
		# -- Affine Scale
		sxy = affine_transform(txy, tmatrix_scale(sx, sy, dx, dy))
		
		# -- Slant back and return
		rxy = asarray([sxy[:,0] + sxy[:,1] * tan(rad), sxy[:,1]]).T

		return rxy

	
		


	