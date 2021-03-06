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

import numpy as np

import common
import utilities_statistics as us

mlow = 10
mupp = 15
dm = 0.2
mbins = np.arange(mlow,mupp,dm)
xmf = mbins + dm/2.0

def prepare_data(hdf5_data, index, massgal, massbar, massbar_inside):

    Omegab = 0.0491
    OmegaM = 0.3121

    (h0, _, mdisk, mbulge, mBH, mgas, mgas_bulge, mhot,
     mreheated, mhalo, typeg) = hdf5_data
     
    ind = np.where((typeg <= 0) & (mdisk+mbulge > 0))
    massgal[index,:] = us.wmedians(x=np.log10(mhalo[ind]) - np.log10(float(h0)),
                                   y=np.log10(mdisk[ind]+mbulge[ind]) - np.log10(float(h0)),
                                   xbins=xmf)
    massbar[index,:] = us.wmedians(x=np.log10(mhalo[ind]) - np.log10(float(h0)),
                                   y=np.log10(mdisk[ind]+mbulge[ind]+mBH[ind]+mgas[ind]+mgas_bulge[ind]+mhot[ind]+mreheated[ind]) - np.log10(mhalo[ind]) - np.log10(Omegab/(OmegaM-Omegab)),
                                   xbins=xmf)
    massbar_inside[index,:] = us.wmedians(x=np.log10(mhalo[ind]) - np.log10(float(h0)),
                                   y=np.log10(mdisk[ind]+mbulge[ind]+mBH[ind]+mgas[ind]+mgas_bulge[ind]+mhot[ind]) - np.log10(mhalo[ind]) - np.log10(Omegab/(OmegaM-Omegab)),
                                   xbins=xmf)


def plot_SMHM_z(plt, outdir, z, massgal):

    fig = plt.figure(figsize=(9.7,11.7))
    xtit = "$\\rm log_{10} (\\rm M_{\\rm halo, DM}/M_{\odot})$"
    ytit = "$\\rm log_{10} (\\rm M_{\\star}/M_{\odot})$"
    xmin, xmax, ymin, ymax = 10.5, 15, 7, 13
    xleg = xmin + 0.2 * (xmax - xmin)
    yleg = ymax - 0.1 * (ymax - ymin)

    #Moster et al. (2013) abundance matching SMHM relation
    M10 = 11.590
    M11 = 1.195
    N10 = 0.0351
    N11 = -0.0247
    beta10 = 1.376
    beta11 = -0.826
    gamma10 = 0.608
    gamma11 = 0.329

    subplots = (321, 322, 323, 324, 325, 326)
    all_labels = (('Shark', 'Moster+13', 'Behroozi+13'), )

    for i, (z, subplot) in enumerate(zip(z, subplots)):
        labels = all_labels[0]
        
        # z=0 ##################################
        ax = fig.add_subplot(subplot)
        common.prepare_ax(ax, xmin, xmax, ymin, ymax, xtit, ytit, locators=(0.1, 1, 0.1))

        ax.tick_params(labelsize=13)
        ax.text(xleg, yleg, 'z=%s' % str(z))

        #Predicted SMHM
        ind = np.where(massgal[i,0,:] != 0)
        xplot = xmf[ind]
        yplot = massgal[i,0,ind]
        errdn = massgal[i,1,ind]
        errup = massgal[i,2,ind]
    
        if not labels:
            ax.errorbar(xplot, yplot[0], color='k')
            ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='grey', interpolate=True)
            ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='grey', interpolate=True)
        else:
            ax.errorbar(xplot, yplot[0], color='k', label=labels[0])
            ax.fill_between(xplot,yplot[0],yplot[0]-errdn[0], facecolor='grey', interpolate=True)
            ax.fill_between(xplot,yplot[0],yplot[0]+errup[0], facecolor='grey', interpolate=True)

        M1 = pow(10.0, M10 + M11 * z/(z+1))
        N = N10 + N11 * z/(z+1)
        beta = beta10 + beta11 * z/(z+1)
        gamma = gamma10 + gamma11 * z/(z+1)

        mh = pow(10.0,xmf)
        m = mh * 2*N * pow (( pow(mh/M1, -beta ) + pow(mh/M1, gamma)), -1)

        if not labels:
            ax.plot(xmf,np.log10(m),'r', linestyle='dashed', linewidth=3)
        else:
            ax.plot(xmf,np.log10(m),'r', linestyle='dashed', linewidth=3, label=labels[1])

        a = 1.0/(1.0+z)
        nu = np.exp(-4*a*a)
        log_epsilon = -1.777 + (-0.006*(a-1)) * nu
        M1= 11.514 + ( - 1.793 * (a-1) - 0.251 * z) * nu
        alpha = -1.412 + 0.731 * nu * (a-1)
        delta = 3.508 + (2.608*(a-1)-0.043 * z) * nu
        gamma = 0.316 + (1.319*(a-1)+0.279 * z) * nu
        Min = xmf-M1
        fx = -np.log10(pow(10,alpha*Min)+1.0)+ delta * pow(np.log10(1+np.exp(Min)),gamma) / (1+np.exp(pow(10,-Min)))
        f = -0.3+ delta * pow(np.log10(2.0),gamma) / (1+np.exp(1))

        m = log_epsilon + M1 + fx - f

        if not labels:
            ax.plot(xmf,m, 'b', linestyle='dashdot',linewidth=3)
        else:
            ax.plot(xmf,m, 'b', linestyle='dashdot',linewidth=3, label=labels[2])

        if labels:
            common.prepare_legend(ax, ['r','b','k'], loc=4)


    common.savefig(outdir, fig, 'SMHM_z.pdf')



def plot_BMHM_z(plt, outdir, massbar, massbar_inside):

    fig = plt.figure(figsize=(5,6))
    xtit = ""
    ytit = ""
    xmin, xmax, ymin, ymax = 10, 15, -1, 1
    xleg = xmax - 0.2 * (xmax - xmin)
    yleg = ymin + 0.15 * (ymax - ymin)

    ax = fig.add_subplot(311)
    plt.subplots_adjust(left=0.17)

    common.prepare_ax(ax, xmin, xmax, ymin, ymax, xtit, ytit, locators=(0.1, 1, 0.1))
    ax.text(xleg, yleg, 'z=0')

    #Predicted SMHM
    ind = np.where(massbar[0,0,:] != 0)
    xplot = xmf[ind]
    yplot = massbar[0,0,ind]
    errdn = massbar[0,1,ind]
    errup = massbar[0,2,ind]

    ax.errorbar(xplot,yplot[0],color='k', label="all baryons")
    ax.errorbar(xplot,yplot[0],yerr=[errdn[0],errup[0]], ls='None', mfc='None', ecolor = 'k', mec='k',marker='+',markersize=2)

    ind = np.where(massbar_inside[0,0,:] != 0)
    xplot = xmf[ind]
    yplot = massbar_inside[0,0,ind]
    errdn = massbar_inside[0,1,ind]
    errup = massbar_inside[0,2,ind]

    ax.plot(xplot,yplot[0],color='b', linestyle='dotted', label="inside halos")
   
    xline = [10.0, 15.0]
    yline = [0.0, 0.0]
    ax.plot(xline,yline,'r', linestyle='dashed')

    common.prepare_legend(ax, ['b','k'], loc=2)

    # z=0.5 ##################################
    #ax = fig.add_subplot(222)
    #common.prepare_ax(ax, xmin, xmax, ymin, ymax, xtit, ytit, locators=(0.1, 1, 0.1))
    #ax.text(xleg,yleg, 'z=0.5')

    #Predicted SMHM
    #ind = np.where(massbar[1,0,:] != 0)
    #xplot = xmf[ind]
    #yplot = massbar[1,0,ind]
    #errdn = massbar[1,1,ind]
    #errup = massbar[1,2,ind]

    #ax.errorbar(xplot,yplot[0],color='k', label="Shark")
    #ax.errorbar(xplot,yplot[0],yerr=[errdn[0],errup[0]], ls='None', mfc='None', ecolor = 'k', mec='k',marker='+',markersize=2)

    #ax.plot(xmf,xmf,'r', linestyle='dashed')


    # z=1 ##################################
    ax = fig.add_subplot(312)
    xtit = ""
    ytit = "$\\rm log_{10} (\\rm M_{\\rm bar}(\\Omega_{\\rm DM}/\\Omega_{\\rm b})/\\rm M_{\\rm halo, DM})$"

    common.prepare_ax(ax, xmin, xmax, ymin, ymax, xtit, ytit, locators=(0.1, 1, 0.1))
    ax.text(xleg, yleg, 'z=1')

    # Predicted SMHM
    ind = np.where(massbar[2,0,:] != 0)
    xplot = xmf[ind]
    yplot = massbar[2,0,ind]
    errdn = massbar[2,1,ind]
    errup = massbar[2,2,ind]

    ax.errorbar(xplot,yplot[0],color='k', label="Shark")
    ax.errorbar(xplot,yplot[0],yerr=[errdn[0],errup[0]], ls='None', mfc='None', ecolor = 'k', mec='k',marker='+',markersize=2)

    ind = np.where(massbar_inside[2,0,:] != 0)
    xplot = xmf[ind]
    yplot = massbar_inside[2,0,ind]
    errdn = massbar_inside[2,1,ind]
    errup = massbar_inside[2,2,ind]

    ax.plot(xplot,yplot[0],color='b', linestyle='dotted')

    ax.plot(xline,yline,'r', linestyle='dashed')


    # z=1 ##################################
    ax = fig.add_subplot(313)
    xtit = "$\\rm log_{10} (\\rm M_{\\rm halo, DM}/M_{\odot})$"
    ytit = ""

    common.prepare_ax(ax, xmin, xmax, ymin, ymax, xtit, ytit, locators=(0.1, 1, 0.1))
    ax.text(xleg,yleg, 'z=2')

    #Predicted SMHM
    ind = np.where(massbar[3,0,:] != 0)
    xplot = xmf[ind]
    yplot = massbar[3,0,ind]
    errdn = massbar[3,1,ind]
    errup = massbar[3,2,ind]

    ax.errorbar(xplot,yplot[0],color='k', label="Shark")
    ax.errorbar(xplot,yplot[0],yerr=[errdn[0],errup[0]], ls='None', mfc='None', ecolor = 'k', mec='k',marker='+',markersize=2)

    ind = np.where(massbar_inside[3,0,:] != 0)
    xplot = xmf[ind]
    yplot = massbar_inside[3,0,ind]
    errdn = massbar_inside[3,1,ind]
    errup = massbar_inside[3,2,ind]

    ax.plot(xplot,yplot[0],color='b', linestyle='dotted')

    ax.plot(xline,yline,'r', linestyle='dashed')

    common.savefig(outdir, fig, 'BMHM_z.pdf')


def main(modeldir, outdir, redshift_table, subvols):

    plt = common.load_matplotlib()
    fields = {'galaxies': ('mstars_disk', 'mstars_bulge', 'm_bh', 'mgas_disk',
                           'mgas_bulge', 'mhot', 'mreheated', 'mvir_hosthalo',
                           'type')}

    zlist = (0, 0.5, 1, 2, 3, 4)
    snapshots = redshift_table[zlist]
    massgal = np.zeros(shape = (len(zlist), 3, len(xmf)))
    massbar = np.zeros(shape = (len(zlist), 3, len(xmf)))
    massbar_inside =  np.zeros(shape = (len(zlist), 3, len(xmf)))

    for idx, snapshot in enumerate(snapshots):
        hdf5_data = common.read_data(modeldir, snapshot, fields, subvols)
        prepare_data(hdf5_data, idx, massgal, massbar, massbar_inside)

    plot_SMHM_z(plt, outdir, zlist, massgal)
    plot_BMHM_z(plt, outdir, massbar, massbar_inside)


if __name__ == '__main__':
    main(*common.parse_args(requires_observations=False))
