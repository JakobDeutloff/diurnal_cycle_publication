# %%
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from src.read_data import read_ccic_histograms, read_gpm_histograms

# %% load hists
hists = {}
hists['ccic'] = read_ccic_histograms("all")
hists['gpm'] = read_gpm_histograms("all")

# %% calculate  Tb(I) from histograms
area_fractions = {}
dim = {'ccic': 'iwp', 'gpm': 'bt'}
for name in ["ccic", "gpm"]:
    area_fractions[name] = hists[name]["hist"].sum(["local_time"]) / hists[name]['hist'].sum(['local_time', dim[name]])

bt_of_iwp = xr.zeros_like(area_fractions["ccic"])
bt_of_iwp['iwp'] = bt_of_iwp['iwp'][::-1]


def interp_bt_of_iwp(t):
    ccic_af = area_fractions["ccic"].sel(time=t)[::-1].cumsum("iwp").values
    gpm_af = area_fractions["gpm"].sel(time=t).cumsum("bt").values
    gpm_bt = area_fractions["gpm"].sel(time=t)["bt"].values
    return np.interp(ccic_af, gpm_af, gpm_bt)


times = area_fractions["ccic"]["time"].values
for t in tqdm(times):
    bt_of_iwp.loc[dict(time=t)] = interp_bt_of_iwp(t)

# %% plot bt of iwp
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(bt_of_iwp['iwp'], bt_of_iwp.mean("time"), color="k", label="Mean")
ax.set_yticks(bt_of_iwp.mean("time").sel(iwp=[10, 1, 0.1], method="nearest").values.round(0))
ax.set_xscale("log")
ax.set_xlim(5e-2, 2e1)
ax.set_ylim(190, 270)
ax.spines[["top", "right"]].set_visible(False)
ax.set_xlabel("$I$ / kg m$^{-2}$")
ax.set_ylabel("$T_{\mathrm{b}}$ / K")
fig.tight_layout()
fig.savefig("plots/bt_of_iwp_area.pdf", bbox_inches='tight')

# %%
