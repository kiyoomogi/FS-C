import numpy

__all__ = [
    "fault_normal",
    "normal_stress",
    "rotation_matrix",
    "rotate_tensor",
]


def fault_normal(strike, dip):
    """
    Return fault normal vector given fault strike and dip angles.

    Parameters
    ----------
    strike : scalar
        Strike angle (between 0 and 360 degrees).
    dip : scalar
        Dip angle (between 0 and 90 degrees).

    Returns
    -------
    array_like
        Fault normal vector.

    """
    if not (0.0 <= strike <= 360.0):
        raise ValueError("strike must be between [ 0, 360 ] degrees.")
    if not (0.0 <= dip <= 90.0):
        raise ValueError("dip must be between [ 0, 90 ] degrees.")

    theta = numpy.deg2rad(strike)
    delta = numpy.deg2rad(dip)
    return numpy.array(
        [
            -numpy.cos(theta) * numpy.sin(delta),
            numpy.sin(theta) * numpy.sin(delta),
            numpy.cos(delta),
        ]
    )


def normal_stress(stress, normal, return_shear=False):
    """
    Return normal stress(es) given stress tensor(s) and normal vector.

    Parameters
    ----------
    stress : array_like
        Stress tensor (3 by 3 matrix) or list of stress tensors.
    normal : array_like
        Normal vector.
    return_shear : bool, optional, default False
        If `True`, also return shear stress.

    Returns
    -------
    scalar or array_like
        Normal stress or list of normal stresses.
    scalar or array_like
        Shear stress or list of shear stresses. Only if ``return_shear == True``.

    """
    if not isinstance(stress, numpy.ndarray):
        raise TypeError()
    cond1 = stress.ndim == 2 and stress.shape == (3, 3)
    cond2 = stress.ndim == 3 and stress[0].shape == (3, 3)
    if not (cond1 or cond2):
        raise ValueError(
            "stress must be a tensor (3 by 3 matrix) or a list of tensors."
        )
    if not isinstance(normal, (list, tuple, numpy.ndarray)):
        raise TypeError()
    if len(normal) != 3:
        raise ValueError("normal must be a vector (3 components).")

    stress_vector = numpy.dot(stress, normal)
    stress_normal = numpy.dot(stress_vector, normal)

    if return_shear:
        axis = 0 if stress_vector.ndim == 1 else 1
        svec_mag = (stress_vector * stress_vector).sum(axis=axis)
        snor_mag = stress_normal * stress_normal
        stress_shear = (svec_mag - snor_mag) ** 0.5
        return stress_normal, stress_shear
    else:
        return stress_normal


def rotation_matrix(angle, axis=2):
    """
    Return rotation matrix for input angle and axis.

    Parameters
    ----------
    angle : scalar
        Rotation angle.
    axis : int (0, 1 or 2), optional, default 2
        Rotation axis:
         - 0: X axis,
         - 1: Y axis,
         - 2: Z axis.

    Returns
    -------
    array_like
        Rotation matrix.

    """
    if axis not in {0, 1, 2}:
        raise ValueError()

    theta = numpy.deg2rad(angle)
    ct, st = numpy.cos(theta), numpy.sin(theta)
    R = {
        0: numpy.array([[1.0, 0.0, 0.0], [0.0, ct, -st], [0.0, st, ct],]),
        1: numpy.array([[ct, 0.0, st], [0.0, 1.0, 0.0], [-st, 0.0, ct],]),
        2: numpy.array([[ct, -st, 0.0], [st, ct, 0.0], [0.0, 0.0, 1.0],]),
    }
    return R[axis]


def rotate_tensor(tensor, angle, axis=2):
    """
    Rotate a tensor along an axis.

    Parameters
    ----------
    tensor : array_like
        Tensor to rotate.
    angle : scalar
        Rotation angle.
    axis : int (0, 1 or 2), optional, default 2
        Rotation axis:
         - 0: X axis,
         - 1: Y axis,
         - 2: Z axis.

    Returns
    -------
    array_like
        Rotated tensor.

    """
    if not isinstance(tensor, numpy.ndarray):
        raise TypeError()
    if tensor.shape != (3, 3):
        raise ValueError()

    R = rotation_matrix(angle, axis)
    return numpy.dot(numpy.dot(R, tensor), R.T)
