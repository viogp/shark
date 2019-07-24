#
# ICRAR - International Centre for Radio Astronomy Research
# (c) UWA - The University of Western Australia, 2018
# Copyright by UWA (in the framework of the ICRAR)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""HMF plots"""

import numpy as np
import os

import common


##################################

# Constants
GyrToYr = 1e9
Zsun = 0.0127
XH = 0.72
PI = 3.141592654
MpcToKpc = 1e3
c_light = 299792458.0 #m/s

# Mass function initialization

mlow = -30 + 5.0 * np.log10(0.677)
mupp = -10 + 5.0 * np.log10(0.677)
dm = 0.5
mbins = np.arange(mlow,mupp,dm)
xlf   = mbins + dm/2.0

def plot_k_lf_evo(plt, outdir, obsdir, h0, LFs_dust, LFs_nodust):

    vegacorr = 1.85

    volcorr = 3.0*np.log10(h0)
    xlf_obs  = xlf
 
    xtit="$\\rm K-band\, mag\, (AB)$"
    ytit="$\\rm log_{10}(\Phi/{\\rm dex^{-1}} {\\rm Mpc}^{-3})$"

    xmin, xmax, ymin, ymax = -28, -16, -6, -1
    xleg = xmin + 0.2 * (xmax-xmin)
    yleg = ymax - 0.1 * (ymax-ymin)

    fig = plt.figure(figsize=(5,11))

    subplots = (311, 312, 313)
    idx = (0, 1, 2)
    zs  = (0, 1, 3)
    band = 10 #K-band
    labels= ('z=0.5', 'z=1', 'z=3')
   
    for subplot, idx, z in zip(subplots, idx, zs):

        ax = fig.add_subplot(subplot)
        ytitplot = ytit
        if (idx == 2):
            xtitplot = xtit
        else:
            xtitplot = ' '
        common.prepare_ax(ax, xmin, xmax, ymin, ymax, xtitplot, ytitplot, locators=(2, 2, 1, 1))
        ax.text(xleg,yleg, labels[idx])

        if(idx == 0):
           file = obsdir+'/lf/lfKz_pozetti03.data'
           lmP03,p,dpup,dpdn = np.loadtxt(file,usecols=[0,1,2,3],unpack=True)
           yobsP03 = np.log10(p)
           ydnP03  = np.log10(p-dpdn)
           yupP03  = np.log10(p+dpup)
   
           ax.errorbar(lmP03[0:12]+vegacorr, yobsP03[0:12], yerr=[yobsP03[0:12]-ydnP03[0:12],yupP03[0:12]-yobsP03[0:12]], ls='None', mfc='None', ecolor = 'grey', mec='grey',marker='o')

           file = obsdir+'/lf/lfKz_saracco06.data'
           lmS06,p,dp = np.loadtxt(file,usecols=[0,1,2],unpack=True)
           yobsS06 = np.log10(p)
           ydnS06  = np.log10(p-dp)
           yupS06  = np.log10(p+dp)
   
           ax.errorbar(lmS06[0:10]+vegacorr, yobsS06[0:10], yerr=[yobsS06[0:10]-ydnS06[0:10],yupS06[0:10]-yobsS06[0:10]], ls='None', mfc='None', ecolor = 'grey', mec='grey',marker='s')


           file = obsdir+'/lf/lfKz_cirasuolo10.data'
           lmC10dn,lmC10up,p,dpup,dpdn, zC10 = np.loadtxt(file,usecols=[0,1,2,3,4,5],unpack=True)
           lmC10 = (lmC10dn+lmC10up)/2.0
           yobsC10 = p
           ydnC10  = p-dpdn
           yupC10  = p+dpup
   
           ax.errorbar(lmC10[0:13]+vegacorr, yobsC10[0:13], yerr=[yobsC10[0:13]-ydnC10[0:13],yupC10[0:13]-yobsC10[0:13]], ls='None', mfc='None', ecolor = 'grey', mec='grey',marker='^')

        if(idx == 1):
           ax.errorbar(lmP03[13:20]+vegacorr, yobsP03[13:20], yerr=[yobsP03[13:20]-ydnP03[13:20],yupP03[13:20]-yobsP03[13:20]], ls='None', mfc='None', ecolor = 'grey', mec='grey',marker='o', label="Pozetti+2003")
           ax.errorbar(lmS06[11:17]+vegacorr, yobsS06[11:17], yerr=[yobsS06[11:17]-ydnS06[11:17],yupS06[11:17]-yobsS06[11:17]], ls='None', mfc='None', ecolor = 'grey', mec='grey',marker='s', label="Saracco+2006")
           ax.errorbar(lmC10[14:25]+vegacorr, yobsC10[14:25], yerr=[yobsC10[14:25]-ydnC10[14:25],yupC10[14:25]-yobsC10[14:25]], ls='None', mfc='None', ecolor = 'grey', mec='grey',marker='^', label="Cirasouolo+2010")

        if(idx == 2):
           ax.errorbar(lmP03[21:26]+vegacorr, yobsP03[21:26], yerr=[yobsP03[21:26]-ydnP03[21:26],yupP03[21:26]-yobsP03[21:26]], ls='None', mfc='None', ecolor = 'grey', mec='grey',marker='o')
           ax.errorbar(lmS06[18:22]+vegacorr, yobsS06[18:22], yerr=[yobsS06[18:22]-ydnS06[18:22],yupS06[18:22]-yobsS06[18:22]], ls='None', mfc='None', ecolor = 'grey', mec='grey',marker='s')
           ax.errorbar(lmC10[52:58]+vegacorr, yobsC10[52:58], yerr=[yobsC10[52:58]-ydnC10[52:58],yupC10[52:58]-yobsC10[52:58]], ls='None', mfc='None', ecolor = 'grey', mec='grey',marker='^')

        #Predicted LF
        if(idx == 0):
            ind = np.where(LFs_dust[z,4,band,:] < 0.)
            y = LFs_dust[z,4,band,ind]+volcorr-np.log10(dm)
            ax.plot(xlf_obs[ind],y[0],'k', linewidth=3, label ='Shark')
            ind = np.where(LFs_nodust[z,4,band,:] < 0.)
            y = LFs_nodust[z,4,band,ind]+volcorr-np.log10(dm)
            ax.plot(xlf_obs[ind],y[0],'k', linewidth=1,  label ='Shark intrinsic')

            ind = np.where(LFs_dust[z,3,band,:] < 0.)
            y = LFs_dust[z,3,band,ind]+volcorr-np.log10(dm)
            ax.plot(xlf_obs[ind],y[0],'b', linewidth=2, linestyle='dotted', label ='disks')
            ind = np.where(LFs_dust[z,2,band,:] < 0.)
            y = LFs_dust[z,2,band,ind]+volcorr-np.log10(dm)
            ax.plot(xlf_obs[ind],y[0],'r', linewidth=2, linestyle='dashed', label ='bulges')
        else:
            ind = np.where(LFs_dust[z,4,band,:] < 0.)
            y = LFs_dust[z,4,band,ind]+volcorr-np.log10(dm)
            ax.plot(xlf_obs[ind],y[0],'k', linewidth=3)
            ind = np.where(LFs_nodust[z,4,band,:] < 0.)
            y = LFs_nodust[z,4,band,ind]+volcorr-np.log10(dm)
            ax.plot(xlf_obs[ind],y[0],'k', linewidth=1)

            ind = np.where(LFs_dust[z,3,band,:] < 0.)
            y = LFs_dust[z,3,band,ind]+volcorr-np.log10(dm)
            ax.plot(xlf_obs[ind],y[0],'b', linewidth=2, linestyle='dotted')
            ind = np.where(LFs_dust[z,2,band,:] < 0.)
            y = LFs_dust[z,2,band,ind]+volcorr-np.log10(dm)
            ax.plot(xlf_obs[ind],y[0],'r', linewidth=2, linestyle='dashed')
        if idx == 0:
            common.prepare_legend(ax, ['k','k','b','r'], loc=4)
        if idx == 1:
            common.prepare_legend(ax, ['grey','grey','grey'], loc=4)

    common.savefig(outdir, fig, "Kband_luminosity_function_evolution.pdf")


def prepare_data(hdf5_data, phot_data, phot_data_nod, LFs_dust, LFs_nodust, index, nbands, 
                 fdisk_emission, fbulge_m_emission, fbulge_d_emission):
   
    #star_formation_histories and SharkSED have the same number of galaxies in the same order, and so we can safely assume that to be the case.
    #to select the same galaxies in galaxies.hdf5 we need to ask for all of those that have a stellar mass > 0, and then assume that they are in the same order.

    (h0, _, mdisk, mbulge, mhalo, mshalo, typeg, age, 
     sfr_disk, sfr_burst, id_gal) = hdf5_data
   
    #(bulge_diskins_hist, bulge_mergers_hist, disk_hist) = sfh

    #components:
    #(len(my_data), 2, 2, 5, nbands)
    #0: disk instability bulge
    #1: galaxy merger bulge
    #2: total bulge
    #3: disk
    #4: total

    ind = np.where(mdisk + mbulge > 0)
    SEDs_dust = np.zeros(shape = (len(mdisk[ind]), 5, nbands))
    SEDs_nodust = np.zeros(shape = (len(mdisk[ind]), 5, nbands))

    p = 0
    for c in range(0,5):
        indust = phot_data[p]
        innodust = phot_data_nod[p]
        for i in range(0,nbands):
            SEDs_dust[:,c,i] = indust[i,:]
            SEDs_nodust[:,c,i] = innodust[i,:]
        p = p + 1

    for i in range(0,nbands):
        for c in range(0,5):
            #calculate LF with bands with dust
            ind = np.where(SEDs_dust[:,c,i] < -1)
            H, bins_edges = np.histogram(SEDs_dust[ind,c,i],bins=np.append(mbins,mupp))
            LFs_dust[index,c,i,:] = LFs_dust[index,c,i,:] + H

            #calculate LF of intrinsic bands 
            ind = np.where(SEDs_nodust[:,c,i] < -1)
            H, bins_edges = np.histogram(SEDs_nodust[ind,c,i],bins=np.append(mbins,mupp))
            LFs_nodust[index,c,i,:] = LFs_nodust[index,c,i,:] + H


def main(model_dir, outdir, redshift_table, subvols, obsdir):

    # Loop over redshift and subvolumes
    plt = common.load_matplotlib()
    fields = {'galaxies': ('mstars_disk', 'mstars_bulge', 'mvir_hosthalo',
                           'mvir_subhalo', 'type', 'mean_stellar_age', 
                           'sfr_disk', 'sfr_burst', 'id_galaxy')}

    #sfh_fields = {'bulges_diskins': ('star_formation_rate_histories'),
    #              'bulges_mergers': ('star_formation_rate_histories'),
    #              'disks': ('star_formation_rate_histories')}

    Variable_Ext = True

    fields_sed = {'SED/ab_dust': ('bulge_d','bulge_m','bulge_t','disk','total'),}
    fields_sed_nod = {'SED/ab_nodust': ('bulge_d','bulge_m','bulge_t','disk','total')}

    z = (0.5, 1.0, 2.0, 3.0) 
    snapshots = redshift_table[z]

    file_hdf5_sed = "Shark-SED-eagle-rr14.hdf5"
    # Create histogram
    for index, snapshot in enumerate(snapshots):

        hdf5_data = common.read_data(model_dir, snapshot, fields, subvols)
        if(Variable_Ext == False):
           seds = common.read_photometry_data(model_dir, snapshot, fields_sed, subvols)
           seds_nod = common.read_photometry_data(model_dir, snapshot, fields_sed_nod, subvols)
        else:
           seds = common.read_photometry_data_variable_tau_screen(model_dir, snapshot, fields_sed, subvols, file_hdf5_sed)
           seds_nod = common.read_photometry_data_variable_tau_screen(model_dir, snapshot, fields_sed_nod, subvols, file_hdf5_sed)

        nbands = len(seds[0]) 

        if(index == 0):
            LFs_dust     = np.zeros(shape = (len(z), 5, nbands, len(mbins)))
            LFs_nodust   = np.zeros(shape = (len(z), 5, nbands, len(mbins)))

        prepare_data(hdf5_data, seds, seds_nod, LFs_dust, LFs_nodust, index, nbands, 
                     fdisk_emission, fbulge_m_emission, fbulge_d_emission)

        h0, volh = hdf5_data[0], hdf5_data[1]
        if(volh > 0.):
            LFs_dust[index,:]   = LFs_dust[index,:]/volh
            LFs_nodust[index,:] = LFs_nodust[index,:]/volh

    # Take logs
    ind = np.where(LFs_dust > 0.)
    LFs_dust[ind] = np.log10(LFs_dust[ind])

    ind = np.where(LFs_nodust > 0.)
    LFs_nodust[ind] = np.log10(LFs_nodust[ind])

    if(Variable_Ext):
       outdir = os.path.join(outdir, 'eagle-rr14')

    plot_k_lf_evo(plt, outdir, obsdir, h0, LFs_dust, LFs_nodust)

if __name__ == '__main__':
    main(*common.parse_args())