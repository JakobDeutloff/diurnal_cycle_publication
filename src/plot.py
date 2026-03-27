import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors


def definitions():

    colors = {
        "icon": "#1f948a",
        "rcemip": "#ff7f0e",
        "dardar": "brown",
        "two_c_ice": "k",
        "ccic": "purple",
        "spare_ice": "darkgreen",
    }

    labels = {
        "icon": "ICON AP",
        "rcemip": "RCEMIP",
        "dardar": "DARDAR",
        "two_c_ice": "2C-ICE",
        "ccic": "CCIC",
        "spare_ice": "SPARE-ICE",
    }

    linestyles = {
        "icon": "--",
        "rcemip": "--",
        "dardar": "-",
        "two_c_ice": "-",
        "ccic": "-",
        "spare_ice": "-",
    }

    return colors, labels, linestyles


def plot_2d_trend(area_fraction, slopes, area_change, feedback, p_values, feedback_cum, err_cum, dim):

    fig, axes = plt.subplots(2, 5, figsize=(12, 4), sharey='row', height_ratios=[1, 0.05], width_ratios=[2, 2, 2, 2, 1])

    # create colormaps
    # Create a diverging colormap: blue -> white -> red
    colors = ["#0E23E3", "white", "#FF0000"]
    n_bins = 256
    cmap_change = mcolors.LinearSegmentedColormap.from_list(
        "custom_diverging", colors, N=n_bins
    )

    colors = ["#0EC7E3", "white", "#FB06BA"]
    cmap_feedback = mcolors.LinearSegmentedColormap.from_list(
        "custom_diverging_feedback", colors, N=n_bins
    )

    # Get mask of where p_value > 0.05
    mask = p_values.values > 0.05
    local_time_grid, dim_grid = np.meshgrid(
        p_values.local_time.values, p_values[dim].values, indexing="ij"
    )

    # plot slopes
    im_slope = axes[0, 0].pcolor(
        slopes.local_time,
        slopes[dim],
        slopes.T,
        cmap=cmap_change,
        vmin=-6,
        vmax=6,
        rasterized=True,
    )
    axes[0, 0].scatter(
        local_time_grid[mask],
        dim_grid[mask],
        color="black",
        marker="o",
        s=0.5,
        label="p > 0.05",
    )

    # plot area fraction
    im_hist = axes[0, 1].pcolor(
        area_fraction.local_time,
        area_fraction[dim],
        area_fraction.T,
        cmap="binary_r",
        vmin=0,
        vmax=0.0005,
        rasterized=True,
    )

    # plot area change
    im_weighted = axes[0, 2].pcolor(
        area_change.local_time,
        area_change[dim],
        area_change.T,
        cmap=cmap_change,
        vmin=-7e-6,
        vmax=7e-6,
        rasterized=True,
    )
    axes[0, 2].scatter(
        local_time_grid[mask],
        dim_grid[mask],
        color="black",
        marker="o",
        s=0.5,
        label="p > 0.05",
    )

    # plot feedback
    im_feedback = axes[0, 3].pcolor(
        feedback.local_time,
        feedback[dim],
        feedback.T,
        cmap=cmap_feedback,
        vmin=-0.006,
        vmax=0.006,
        rasterized=True,
    )
    axes[0, 3].scatter(
        local_time_grid[mask & (local_time_grid >=6) & (local_time_grid <=18)],
        dim_grid[mask & (local_time_grid >=6) & (local_time_grid <=18)],
        color="black",
        marker="o",
        s=0.5,
        label="p > 0.05",
    )

    # plot cumsum of feedback
    axes[0, 4].plot(
        feedback_cum,
        feedback_cum[dim],
        color="k",
        label="Cumulative Feedback",
    )
    axes[0, 4].fill_betweenx(
        feedback_cum[dim],
        feedback_cum - err_cum,
        feedback_cum + err_cum,
        color="gray",
        alpha=0.5,
    )
    axes[0, 4].spines[["top", "right"]].set_visible(False)
    axes[0, 4].set_xlabel(r"$\sum_{I}$ $\lambda$ / W m$^{-2}$ K$^{-1}$")
    axes[0, 4].set_xticks([0, np.round(feedback_cum.isel({dim:-1}).values, 2)])

    if dim == "bt":
        for ax in axes[0,:-1]:
            ax.set_xlabel("Local Time / h")
            ax.set_ylim([200, 260])
            ax.set_yticks([200, 230, 260])
        axes[0, 0].set_ylabel(r"$T_{\mathrm{b}}$ / K")
    else:
        for ax in axes[0,:-1]:
            ax.set_yscale("log")
            ax.invert_yaxis()
            ax.set_ylim([10, 1e-1])
        axes[0, 0].set_ylabel("$I$ / kg m$^{-2}$")

    for ax in axes[0, :-1]:
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_xticks([6, 12, 18])
        ax.set_xlabel("Local Time / h")

    cb1 = fig.colorbar(
        im_slope,
        cax=axes[1, 0],
        label=r"$\dfrac{\mathrm{d}f}{f~\mathrm{d}T}$ / % K$^{-1}$",
        extend="both",
        orientation="horizontal",
    )
    cb1.set_ticks([-6, 0, 6])
    cb2 = fig.colorbar(
        im_hist,
        cax=axes[1, 1],
        label="$f$",
        extend="max",
        orientation="horizontal",
    )
    cb2.set_ticks([0, 0.00025, 0.0005])
    cb3 = fig.colorbar(
        im_weighted,
        cax=axes[1, 2],
        label=r"$\dfrac{\mathrm{d}f}{\mathrm{d}T}$ / K$^{-1}$",
        extend="both",
        orientation="horizontal",
    )
    cb3.set_ticks([-7e-6, 0, 7e-6])
    cb4 = fig.colorbar(
        im_feedback,
        cax=axes[1, 3],
        label="$\lambda$ / W m$^{-2}$ K$^{-1}$",
        extend="both",
        orientation="horizontal",
    )
    cb4.set_ticks([-0.006, 0, 0.006])
    axes[1, 4].remove()

    # add letters 
    for ax, letter in zip(axes[0, :], ["a", "b", "c", "d", "e"]):
        ax.text(
            0.08,
            0.88,
            letter,
            transform=ax.transAxes,
            fontsize=22,
            fontweight="bold",
        )

    fig.tight_layout()
    return fig, axes