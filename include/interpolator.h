//
// ICRAR - International Centre for Radio Astronomy Research
// (c) UWA - The University of Western Australia, 2017
// Copyright by UWA (in the framework of the ICRAR)
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.
//

/**
 * @file
 */

#ifndef SHARK_INTERPOLATION_H_
#define SHARK_INTERPOLATION_H_

#include <memory>
#include <vector>

#include <gsl/gsl_interp2d.h>
#include <gsl/gsl_spline2d.h>

#include "utils.h"

namespace shark {

/// A deleter of gsl_interp2d objects
using gsl_interp2d_deleter = deleter<gsl_interp2d, gsl_interp2d_free>;

/// A deleter of gsl_interp_accel objects
using gsl_interp_accel_deleter = deleter<gsl_interp_accel, gsl_interp_accel_free>;

/// A 2D interpolation object
class Interpolator {

public:

	enum InterpolatorType {
		BILINEAR = 0,
		BICUBIC,
	};

	Interpolator(std::vector<double> xvals, std::vector<double> yvals,
	             std::vector<double> zvals, InterpolatorType type = BILINEAR);

	/// Copy constructor
	Interpolator(const Interpolator &other);

	double get(double x, double y) const;

private:
	std::unique_ptr<gsl_interp2d, gsl_interp2d_deleter> interp2d;
	std::unique_ptr<gsl_interp_accel, gsl_interp_accel_deleter> xacc;
	std::unique_ptr<gsl_interp_accel, gsl_interp_accel_deleter> yacc;
	const gsl_interp2d_type *type;
	std::vector<double> x;
	std::vector<double> y;
	std::vector<double> z;

	void _init_gsl_objects();
	const gsl_interp2d_type *to_gsl(InterpolatorType type) const;
};

}  // namespace shark

#endif // SHARK_INTERPOLATION_H_