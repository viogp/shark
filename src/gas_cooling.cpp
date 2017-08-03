/*
 * gas_cooling.cpp
 *
 *  Created on: 17May,2017
 *      Author: clagos
 */

#include <cmath>
#include <fstream>
#include <map>
#include <tuple>

#include <gsl/gsl_interp2d.h>
#include <gsl/gsl_spline2d.h>

#include "cosmology.h"
#include "gas_cooling.h"
#include "logging.h"
#include "numerical_constants.h"
#include "components.h"

using namespace std;

namespace shark {

GasCoolingParameters::GasCoolingParameters(const std::string &filename) :
	Options(filename),
	rcore(0),
	model(CROTON06),
	lambdamodel(CLOUDY),
	cooling_table()
{
	string cooling_tables_dir;
	load("gas_cooling.model", model);
	load("gas_cooling.rcore", rcore);
	load("gas_cooling.lambdamodel", lambdamodel);
	load("gas_cooling.cooling_tables_dir", cooling_tables_dir, true);

	tables_idx metallicity_tables = find_tables(cooling_tables_dir);
	load_tables(cooling_tables_dir, metallicity_tables);
}

GasCoolingParameters::tables_idx GasCoolingParameters::find_tables(
	const string &cooling_tables_dir)
{
	//read cooling tables and load values in
	string prefix;
	if (lambdamodel == CLOUDY) {
		prefix = "C08.00_";
	}
	else if (lambdamodel == SUTHERLAND) {
		prefix = "S93_";
	}

	string tables = cooling_tables_dir + "/" + prefix + "tables.txt";

	// Collect metallicity tables information
	LOG(debug) << "Reading metallicity table index" << tables;
	string line;
	map<double, string> metallicity_tables;
	ifstream f = open_file(tables);
	while ( getline(f, line) ) {

		trim(line);
		if (is_skipable(line)) {
			continue;
		}

		double metallicity;
		string table_fname;
		istringstream iss(line);
		iss >> metallicity >> table_fname;
		trim(table_fname);

		metallicity_tables[metallicity] = table_fname;
	}
	f.close();

	return metallicity_tables;
}

void GasCoolingParameters::load_tables(
	const string &cooling_tables_dir,
	const tables_idx &metallicity_tables)
{

	// Populate cooling_table
	for(auto &kv: metallicity_tables) {

		double metallicity = std::get<0>(kv);
		const string fname = cooling_tables_dir + "/" + std::get<1>(kv);

		LOG(debug) << "Reading table " << fname << " for metallicity " << metallicity;

		ifstream f = open_file(fname);
		string line;
		while ( getline(f, line) ) {

			trim(line);
			if (is_skipable(line)) {
				continue;
			}

			double t, ne, nh, nt, logl;
			istringstream iss(line);
			iss >> t >> ne >> nh >> nt >> logl;

			cooling_table.log10lam.push_back(logl);
			cooling_table.log10temp.push_back(t);
			cooling_table.zmetal.push_back(metallicity);

		}
		f.close();
	}
}

namespace detail {

template <>
GasCoolingParameters::LambdaCoolingModel Helper<GasCoolingParameters::LambdaCoolingModel>::get(const std::string &name, const std::string &value) {
	if ( value == "cloudy" ) {
		return GasCoolingParameters::CLOUDY;
	}
	else if ( value == "sutherland" ) {
		return GasCoolingParameters::SUTHERLAND;
	}
	std::ostringstream os;
	os << name << " option value invalid: " << value << ". Supported values are cloudy and sutherland";
	throw invalid_option(os.str());
}


template <>
GasCoolingParameters::CoolingModel Helper<GasCoolingParameters::CoolingModel>::get(const std::string &name, const std::string &value) {
	if ( value == "Croton06" ) {
		return GasCoolingParameters::CROTON06;
	}
	else if ( value == "Benson10" ) {
		return GasCoolingParameters::BENSON10;
	}
	std::ostringstream os;
	os << name << " option value invalid: " << value << ". Supported values are Croton06 and Galform";
	throw invalid_option(os.str());
}

} // namespace detail

GasCooling::GasCooling(GasCoolingParameters parameters, ReionisationParameters reio_parameters, std::shared_ptr<Cosmology> cosmology, std::shared_ptr<AGNFeedback> agnfeedback) :
	parameters(parameters),
	reio_parameters(reio_parameters),
	cosmology(cosmology),
	agnfeedback(agnfeedback),
	interp(nullptr)
{
	interp.reset(gsl_interp2d_alloc(gsl_interp2d_bilinear, parameters.cooling_table.log10temp.size(), parameters.cooling_table.zmetal.size()));
}

double GasCooling::cooling_rate(Subhalo &subhalo, double z, double deltat) {

	using namespace constants;

    gsl_interp_accel *xacc = gsl_interp_accel_alloc();
    gsl_interp_accel *yacc = gsl_interp_accel_alloc();

    double coolingrate;

    /**
     * For now assume that gas can cool only in central subhalos.
     */
    if(subhalo.subhalo_type == Subhalo::CENTRAL){


    	/**
    	 * Plant black hole seed if necessary
    	 */
    	agnfeedback->plant_seed_smbh(subhalo);

    	//Calculate Eddington luminosity of BH in central galaxy.

    	double Ledd = agnfeedback->eddington_luminosity(subhalo.galaxies[0]->smbh.mass);


    	/**
    	 * Test for subhalos that are affected by reionisation
    	 */
    	if(subhalo.Vvir < reio_parameters.vcut && z < reio_parameters.zcut){
    		return 0;
    	}
    	else {
    		//TODO: see if here it should be total mass for both Croton and Benson models.
    		/**
    		 * We need to convert masses and velocities to physical units before proceeding with calculation.
    		 */
    		double mhot = cosmology->comoving_to_physical_mass(subhalo.hot_halo_gas.mass+subhalo.cold_halo_gas.mass+subhalo.ejected_galaxy_gas.mass);
    		double mzhot = cosmology->comoving_to_physical_mass(subhalo.hot_halo_gas.mass_metals+subhalo.cold_halo_gas.mass_metals+subhalo.ejected_galaxy_gas.mass_metals);

    		double vvir = cosmology->comoving_to_physical_velocity(subhalo.Vvir, z);
    		double mvir = cosmology->comoving_to_physical_mass(subhalo.Mvir);

    		double zhot = (mzhot/mhot);

    		double Tvir = 35.9*std::pow(vvir,2); //in K.
    		double lgTvir = log10(Tvir); //in K.

    		double Rvir = constants::G*mvir/std::pow(vvir,2); //in Mpc.

    		/**
    		 * Calculates the cooling Lambda function for the metallicity and temperature of this halo.
    		 */
    		double logl = gsl_interp2d_eval_extrap(interp.get(), parameters.cooling_table.log10temp.data(), parameters.cooling_table.zmetal.data(), parameters.cooling_table.log10lam.data(), lgTvir, zhot, xacc, yacc); //in cgs

			/**
			 * Calculate mean density for notional cooling profile.
			 */
			double nh_density  = mean_density(mhot, Rvir); //in units of cm^-3.

    		double tcool;
    		double tcharac;

    		/**
    		 * This corresponds to the very simple model of Croton06, in which the cooling time is assumed to be equal to the
    		 * dynamical timescale of the halo. With that assumption, and using an isothermal halo, the calculation of rcool and mcool
    		 * is trivial.
    		 */
    		if(parameters.model == GasCoolingParameters::CROTON06)
    		{

    			tcool = Rvir/vvir*constants::KMS2MPCGYR; //in Gyr.

    			tcharac = tcool*constants::GYR2S; //in seconds.

    		}


    		/**
    		 * This corresponds to the GALFORM-like model. Specifically here we are implementing the Benson & Bower (2010) model
    		 * for cooling, which calculated a time available for cooling depending on the integral of the the temperature
    		 * mass and cooling time history.
    		 */

    		if(parameters.model == GasCoolingParameters::BENSON10){

    			tcool = cooling_time(Tvir, logl,nh_density); //cooling time at notional density in Gyr.

    			/**
    			 * Push back the cooling properties at this timestep.
    			 */
    			subhalo.cooling_subhalo_tracking.tcooling.push_back(tcool);
    			subhalo.cooling_subhalo_tracking.temp.push_back(Tvir);
    			subhalo.cooling_subhalo_tracking.deltat.push_back(deltat);
    			//In the case of mass we convert back to comoving units.
    			subhalo.cooling_subhalo_tracking.mass.push_back(cosmology->physical_to_comoving_mass(mhot));

    			double integral = 0.0;//will save integral(T*M/tcool)

    			for(unsigned i=0;i<subhalo.cooling_subhalo_tracking.deltat.size();++i){
    				integral += subhalo.cooling_subhalo_tracking.temp[i]*subhalo.cooling_subhalo_tracking.mass[i]/subhalo.cooling_subhalo_tracking.tcooling[i]*subhalo.cooling_subhalo_tracking.deltat[i];
    			}
    			tcharac = integral/(Tvir*mhot/tcool); //available time for cooling in Gyr.

    		}


    		//I STILL NEED TO ADD A LIMIT TO THE TOTAL RADIATED ENERGY TO THE TOTAL THERMAL ENERGY OF THE HALO. SEE EQ. 18 AND 19 IN BENSON ET AL. (2010).

    		double r_cool = cooling_radius(nh_density,tcharac, logl, Tvir); //in Mpc.

    		if(r_cool < Rvir){
    			//cooling radius smaller than virial radius
    			coolingrate = 0.5*(r_cool/Rvir)*(mhot/tcool); //in Msun/Gyr.
    			r_cool = Rvir;
    		}
    		else {
    			//cooling radius larger than virial radius
    			coolingrate = mhot/tcool;
    		}

    		if(agnfeedback->parameters.model == AGNFeedbackParameters::GALFORM){
    			if(agnfeedback->parameters.alpha_cool > 0){
    				double tdyn_rcool = r_cool/vvir*constants::KMS2MPCGYR; //Dynamical timescale at cooling radius.
        			/**
        			 * Calculate mean density at rcool.
        			 */
        			double nh_rcool  = density_shell(mhot, Rvir, r_cool); //in units of cm^-3.

        			double tcool_rcool = cooling_time(Tvir, logl, nh_rcool); //cooling time at rcool in Gyr.

        			double timescale_ratio = tcool_rcool/tdyn_rcool;

        			/**
        			 * Now we compare the cooling timescale with the dynamical timescale at rcool to
        			 * find out if galaxy is in hot halo mode. Only galaxies in the hot halo regime are
        			 * eligible for (radio) AGN fedback.
        			 */
        			if(timescale_ratio > 1/agnfeedback->parameters.alpha_cool){
        				//Halo is eligible for AGN feedback.
        				//Calculate cooling luminosity.
        				double Lcool = cooling_luminosity(logl, r_cool, Rvir, mhot);

        				if(Lcool < agnfeedback->parameters.f_edd * Ledd){
        					subhalo.galaxies[0]->smbh.macc = agnfeedback->accretion_rate_hothalo_smbh(Lcool, subhalo.galaxies[0]->smbh.mass);
        					//now convert mass accretion rate to comoving units.
        					subhalo.galaxies[0]->smbh.macc = cosmology->physical_to_comoving_mass(subhalo.galaxies[0]->smbh.macc);

        		    		// set cooling rate to 0.
        					coolingrate = 0;
        				}

        			}//end if of hot halo mode.
    			}// end if of AGN feedback model
    		}// end if of GALFORM AGN feedback model.
    		else if(agnfeedback->parameters.model == AGNFeedbackParameters::LGALAXIES){
    			//a pseudo cooling luminosity k*T/lambda(T,Z)
    			double Lpseudo_cool = constants::k_Boltzmann_erg * Tvir / std::pow(10,logl) / std::pow(10,40);

    			subhalo.galaxies[0]->smbh.macc = agnfeedback->accretion_rate_hothalo_smbh(Lpseudo_cool, subhalo.galaxies[0]->smbh.mass);
				//now convert mass accretion rate to comoving units.
				subhalo.galaxies[0]->smbh.macc = cosmology->physical_to_comoving_mass(subhalo.galaxies[0]->smbh.macc);

	    		//Mass heating rate from AGN in units of Msun/Gyr.
	    		double mheatrate = agnfeedback->agn_bolometric_luminosity(subhalo.galaxies[0]->smbh.macc)/(0.5*std::pow(vvir*KM2CM,2))*MACCRETION_cgs_simu;

	    		//modify cooling rate according to heating rate.
	    		if(mheatrate < coolingrate){
	    			coolingrate = (1-mheatrate/coolingrate)*coolingrate;
	    		}
	    		else{
	    			/*CHECK: If mheatrate is > than cooling rate, then one needs to truncate the BH accretion rate to match that heating rate?*/
	    			coolingrate = 0;
	    		}

    		}
    		else{//In the case none of the two models above are included.
    			subhalo.galaxies[0]->smbh.macc = 0;
    		}

    		/**
    		 * Now, we modify the SMBH mass and metals, and the hot gas mass accordingly.
    		 */
    		if(subhalo.galaxies[0]->smbh.macc > 0){
    			//Now calculate new BH mass and metals due to gas accretion from hot halo.
				subhalo.galaxies[0]->smbh.mass += subhalo.galaxies[0]->smbh.macc * deltat ;
				subhalo.galaxies[0]->smbh.mass_metals += subhalo.galaxies[0]->smbh.macc * deltat /mhot*mzhot;

	    		/**
	    		 * Update hot halo gas properties as a response of how much the SMBH is accreting;
	    		 */
	    		subhalo.hot_halo_gas.mass -= subhalo.galaxies[0]->smbh.mass;
	    		subhalo.hot_halo_gas.mass_metals -= subhalo.galaxies[0]->smbh.mass_metals;
    		}


    		if(coolingrate > 0){//perform calculations below ONLY if cooling rate >0.
    			/**
    			 * Convert cooling rate back to comoving units. This conversion is only necessary because mass was previously converted to physical.
    			 */
    			coolingrate = cosmology->physical_to_comoving_mass(coolingrate);

    			/**
    			 * Save properties of cooling gas in the halo gas component that tracks the cold gas.
    			 */
    			subhalo.cold_halo_gas.mass = coolingrate*deltat;
    			subhalo.cold_halo_gas.mass_metals = coolingrate*deltat/mhot*mzhot;//fraction of mass in the cold gas is the same as in metals.

    			/**
    			 * Update hot halo gas properties as a response of how much cooling there is in this timestep;
    			 */
    			subhalo.hot_halo_gas.mass -=subhalo.cold_halo_gas.mass;
    			subhalo.hot_halo_gas.mass_metals -= subhalo.cold_halo_gas.mass_metals;
    		}
    		else if(coolingrate < 0){
    			//avoid negative numbers.
    			coolingrate = 0;
    		}

    		return coolingrate;
    	}
    }
    else{
    	//Assume satellite subhalos have 0 cooling rate.
    	return 0;
    }
}

double GasCooling::cooling_time(double Tvir, double logl, double nh_density){

	using namespace constants;

	return 3.0*k_Boltzmann_erg*Tvir/(2.0*std::pow(10,logl)*nh_density)/GYR2S; //cooling time at notional density in Gyr.;
}

double GasCooling::mean_density(double mhot, double rvir){

	using namespace constants;

	return mhot*MSOLAR_g/(SPI*std::pow(rvir*MPC2CM,3.0))/M_Atomic_g; //in units of cm^-3.
}

double GasCooling::cooling_radius(double rho_shell, double tcharac, double logl, double Tvir){

	using namespace constants;

	double denominator_temp = 1.5*M_Atomic_g*mu_Primordial*k_Boltzmann_erg*Tvir; //in cgs
	return pow(rho_shell*tcharac*pow(10,logl)/denominator_temp,0.5)/MPC2CM; //in Mpc.
}

double GasCooling::density_shell(double mhot, double rvir, double r) {

	using namespace constants;

	/**
	 * rho_shell as defined by an isothermal profile.
	 * Any other hot gas profile should modify rho_shell.
	 */
	return mhot*MSOLAR_g /PI4 /(rvir*MPC2CM) / std::pow(r,2); //in cgs.

}

double GasCooling::cooling_luminosity(double logl, double rcool, double rvir, double mhot){

	/**
	 *  This function calculated the cooling luminosity for a given cooling function
	 *  and a notional gas density profile.
	 *
	 */
	using namespace constants;

	if(rcool < rvir){
		double rmin = rcool;
		double rmax = rvir;
		/**
		 * For an isothermal profile, we define mass enclosed between rcool and rvir in csg.
		 */
		double mass_enclosed = mhot /PI4 /rvir * (rvir-rcool) * MSOLAR_g;

		//Define cooling luminosity in $10^{40} erg/s$.
		double Lcool = PI4 * std::pow(10,logl) * mass_enclosed / std::pow(10,40);

		return Lcool;
	}
	else{
		return 0;
	}
}


}  // namespace shark