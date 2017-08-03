/*
 * gas_cooling.h
 *
 *  Created on: 17May,2017
 *      Author: clagos
 */

#ifndef INCLUDE_GAS_COOLING_H_
#define INCLUDE_GAS_COOLING_H_

#include <map>
#include <memory>
#include <string>
#include <vector>


#include <gsl/gsl_math.h>
#include <gsl/gsl_interp2d.h>

#include "options.h"
#include "components.h"
#include "reionisation.h"
#include "agn_feedback.h"

namespace shark {
/**
 * An element of the cooling tables
 */
struct CoolingTable {
	std::vector<double> log10lam;
	std::vector<double> log10temp;
	std::vector<double> zmetal;
};

class GasCoolingParameters : public Options {

public:

	typedef std::map<double, std::string> tables_idx;

	enum LambdaCoolingModel {
		CLOUDY = 0,
		SUTHERLAND
	};

	enum CoolingModel {
		CROTON06 = 0,
		BENSON10
	};

	GasCoolingParameters(const std::string &filename);

	double rcore;
	LambdaCoolingModel lambdamodel;
	CoolingModel model;
	//cooling tables
	CoolingTable cooling_table; //these should be an array of parameters.

private:
	tables_idx find_tables(const std::string &cooling_tables_dir);
	void load_tables(const std::string &cooling_tables_dir, const tables_idx &metallicity_tables);
};


class GasCooling {

public:
	GasCooling(GasCoolingParameters parameters, ReionisationParameters reio_parameters, std::shared_ptr<Cosmology> cosmology, std::shared_ptr<AGNFeedback> agnfeedback);

	double cooling_rate(Subhalo &subhalo, double z, double deltat);
	double cooling_time(double Tvir, double logl, double nh_density);
	double mean_density(double mhot, double rvir);
	double cooling_radius(double rho_shell, double tcharac, double logl, double Tvir);
	double density_shell(double mhot, double rvir, double r);
	double cooling_luminosity(double logl, double rcool, double rvir, double mhot);

private:
	ReionisationParameters reio_parameters;
	GasCoolingParameters parameters;
	std::shared_ptr<Cosmology> cosmology;
	std::shared_ptr<AGNFeedback> agnfeedback;
	std::shared_ptr<gsl_interp2d> interp;

};

}  // namespace shark



#endif /* INCLUDE_GAS_COOLING_H_ */