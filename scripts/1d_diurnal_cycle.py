# %%
import xarray as xr
import matplotlib.pyplot as plt
from src.helper_functions import (
    nan_detrend,
    deseason,
    regress_hist_temp_1d,
)
from src.read_data import read_ccic_histograms, read_gpm_histograms, read_temperature, read_icon
from scipy.signal import detrend


# %% load data
color = {"all": "black", "sea": "blue", "land": "green"}
names = ["all", "sea", "land"]
dims = {"ccic": "iwp", "gpm": "bt"}
hists_ccic = {}
hists_gpm = {}
hists_icon = {}
temps = {}
for name in names:
    hists_ccic[name] = read_ccic_histograms(name)
    hists_gpm[name] = read_gpm_histograms(name)
    temps[name] = read_temperature(name)
hists_icon["plus4K"] = read_icon("jed0022")
hists_icon['control'] = read_icon("jed0011")
    

# %% calculate cloud fraction
cf_ccic = {}
cf_gpm = {}
for name in names:
    cf_ccic[name] = hists_ccic[name]["hist"].sel(iwp=slice(1, None)).sum(
        "iwp"
    ) / hists_ccic[name]["hist"].sum(["iwp", "local_time"])
    cf_gpm[name] = hists_gpm[name]["hist"].sel(bt=slice(None, 231)).sum(
        "bt"
    ) / hists_gpm[name]["hist"].sum(["bt", "local_time"])

# %% normalise  cloud fractions
cf_ccic_norm = {}
cf_gpm_norm = {}
for name in names:
    cf_ccic_norm[name] = cf_ccic[name] / cf_ccic[name].sum("local_time")
    cf_gpm_norm[name] = cf_gpm[name] / cf_gpm[name].sum("local_time")


# %% detrend and deseasonalize
temps_deseason = {}
for name in names:
    temp_detrend = xr.DataArray(
        detrend(temps[name]), coords=temps[name].coords, dims=temps[name].dims
    )
    temps_deseason[name] = deseason(temp_detrend)
cf_ccic_deseason = {}
cf_gpm_deseason = {}
for name in names:
    cf_detrend = nan_detrend(cf_ccic_norm[name], dim="local_time")
    cf_ccic_deseason[name] = deseason(cf_detrend)
    cf_detrend = nan_detrend(cf_gpm_norm[name], dim="local_time")
    cf_gpm_deseason[name] = deseason(cf_detrend)

# %% regression
slopes_ccic = {}
slopes_gpm = {}
err_ccic = {}
err_gpm = {}
for name in names:
    slopes_ccic[name], err_ccic[name] = regress_hist_temp_1d(
        cf_ccic_deseason[name], temps_deseason[name], cf_ccic_norm[name]
    )
    slopes_gpm[name], err_gpm[name] = regress_hist_temp_1d(
        cf_gpm_deseason[name], temps_deseason[name], cf_gpm_norm[name]
    )

# %% calculate change ICON
for run in ['control', 'plus4K']:
    hists_icon[run] = (hists_icon[run].sum("day") / hists_icon[run].sum()).values
slope_icon = (hists_icon['plus4K'] - hists_icon['control']) * 100 / 4 / hists_icon['control']


# %% plot diurnal cycle of both
fig, ax = plt.subplots(figsize=(6, 4))

for name in names:
    ax.plot(
        cf_ccic[name].local_time,
        cf_ccic[name].mean("time"),
        color=color[name],
        linestyle="-",
    )

ax.set_xlim([0, 24])
ax.set_xlabel("Local Time / h")
ax.set_ylabel("$f_{\mathrm{d}}$")
handles = [
    plt.Line2D([0], [0], color="black", linestyle="-"),
    plt.Line2D([0], [0], color="blue", linestyle="-"),
    plt.Line2D([0], [0], color="green", linestyle="-"),]
labels = ["All", "Ocean", "Land"]

ax.legend(handles, labels, frameon=False)
ax.spines[["top", "right"]].set_visible(False)
ax.set_xticks([6, 12, 18])
ax.set_yticks([0.001, 0.002, 0.003])
fig.savefig("mean_dc.pdf", bbox_inches="tight")

# %% calculate total cf
total_cf_ccic = {}
total_cf_gpm = {}
for name in names:
    total_cf_ccic[name] = cf_ccic[name].sum("local_time").mean("time")
    print(f"{name} total ccic cf: {total_cf_ccic[name].values}")

# %% plot change of diurnal cycle
fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
labels = {
    "all": "All",
    "sea": "Ocean",
    "land": "Land",
}
for ax in axes:
    ax.axhline(0, color="black", linewidth=0.5)

for name in ["land", "sea"]:
    axes[1].plot(
        slopes_ccic[name].local_time,
        slopes_ccic[name],
        color=color[name],
        label=f"{labels[name]}",
    )
    axes[1].fill_between(
        slopes_ccic[name].local_time,
        slopes_ccic[name] - err_ccic[name],
        slopes_ccic[name] + err_ccic[name],
        color=color[name],
        alpha=0.3,
    )
axes[0].plot(
    slopes_ccic["all"].local_time,
    slopes_ccic["all"],
    color="black",
    label=f"$I$ All",
    linestyle="-",
)
axes[0].fill_between(
    slopes_ccic["all"].local_time,
    slopes_ccic["all"] - err_ccic["all"],
    slopes_ccic["all"] + err_ccic["all"],
    color="black",
    alpha=0.3,
)
axes[0].plot(
    slopes_gpm["all"].local_time,
    slopes_gpm["all"],
    color="k",
    label=r"$T_{\mathrm{b}}$ All",
    linestyle="--",
)
axes[0].fill_between(
    slopes_gpm["all"].local_time,
    slopes_gpm["all"] - err_gpm["all"],
    slopes_gpm["all"] + err_gpm["all"],
    color="k",
    alpha=0.3,
)
axes[0].plot(
    slopes_ccic["all"].local_time,
    slope_icon,
    color="red",
    label="GSRM +4K",
)

for ax in axes:
    ax.set_xlim([0, 24])
    ax.set_xlabel("Local Time / h")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xticks([6, 12, 18])
    ax.set_yticks([-4, 0, 4])

# add letters
for ax, letter in zip(axes, ["a", "b"]):
    ax.text(
        0.05,
        1,
        letter,
        transform=ax.transAxes,
        fontsize=22,
        fontweight="bold",
        va="top",
    )


axes[0].set_ylabel(
    r"$\dfrac{\mathrm{d}f_{\mathrm{d}}}{f_{\mathrm{d}}~\mathrm{d}T}$ / % K$^{-1}$"
)
fig.tight_layout()

fig.savefig("plots/diurnal_cycle_change_land_sea.pdf")

# %% numbers for paper
print(f"ccic: {slopes_ccic['all'].min()}")
print(f"gpm: {slopes_gpm['all'].min()}")

# %% plot non-normalised change of f_d
# detrend and deseasonalize
cf_ccic_deseason_raw = {}
cf_gpm_deseason_raw = {}
for name in names:
    cf_detrend = nan_detrend(cf_ccic[name], dim="local_time")
    cf_ccic_deseason_raw[name] = deseason(cf_detrend)
    cf_detrend = nan_detrend(cf_gpm[name], dim="local_time")
    cf_gpm_deseason_raw[name] = deseason(cf_detrend)

#regression
slopes_ccic_raw = {}
slopes_gpm_raw = {}
err_ccic_raw = {}
err_gpm_raw = {}
for name in names:
    slopes_ccic_raw[name], err_ccic_raw[name] = regress_hist_temp_1d(
        cf_ccic_deseason_raw[name], temps_deseason[name], cf_ccic[name]
    )
    slopes_gpm_raw[name], err_gpm_raw[name] = regress_hist_temp_1d(
        cf_gpm_deseason_raw[name], temps_deseason[name], cf_gpm[name]
    )

fig, ax = plt.subplots(figsize=(5, 3.5))
ax.axhline(0, color="black", linewidth=0.5)
ax.plot(
    slopes_ccic_raw["all"].local_time,
    slopes_ccic_raw["all"],
    color="black",
    label = f"$I$ All",
)
ax.fill_between(
    slopes_ccic_raw["all"].local_time,
    slopes_ccic_raw["all"] - err_ccic_raw["all"],
    slopes_ccic_raw["all"] + err_ccic_raw["all"],
    color="black",
    alpha=0.3,
)
ax.plot(
    slopes_gpm_raw["all"].local_time,
    slopes_gpm_raw["all"],
    color="k",
    linestyle="--",
    label=r"$T_{\mathrm{b}}$ All",
)
ax.fill_between(
    slopes_gpm_raw["all"].local_time,
    slopes_gpm_raw["all"] - err_gpm_raw["all"],
    slopes_gpm_raw["all"] + err_gpm_raw["all"],
    color="k",
    alpha=0.3,
)

ax.set_xlim([0, 24])
ax.set_xlabel("Local Time / h")
ax.set_ylabel(
    r"$\dfrac{\mathrm{d}f_{\mathrm{d}}}{f_{\mathrm{d}}~\mathrm{d}T}$ / % K$^{-1}$"
)
ax.spines[["top", "right"]].set_visible(False)
ax.set_xticks([6, 12, 18])
ax.legend(frameon=False)
fig.savefig("plots/diurnal_cycle_change_all_nonnormalised.pdf", bbox_inches="tight")

# %%
