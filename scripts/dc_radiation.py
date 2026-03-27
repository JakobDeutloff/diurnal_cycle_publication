# %%
import xarray as xr
import matplotlib.pyplot as plt
from src.read_data import read_sw_in, read_lw_out

# %%
rsdt = read_sw_in()
rlut = read_lw_out()

# %% interpolate to same lt points
rsdt = rsdt.interp(time_points=rlut['local_time'])

# %% plot rlutcs 
fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True, height_ratios=[2, 1])
axes[0].plot(rlut['local_time'], rlut, color='r', label='Upwelling LW')
axes[0].plot(rsdt['time_points'], rsdt, color='b', label='Downwelling SW')
axes[1].plot(rlut['local_time'], rlut, color='r')
axes[1].set_xlabel('Local Time / h')

for ax in axes:
    ax.set_ylabel('Radiative Flux / W m$^{-2}$')
    ax.set_xticks([6, 12, 18])
    ax.spines[['top', 'right']].set_visible(False)

# put letters
for ax, letter in zip(axes, ['a', 'b']):
    ax.text(0.04, 1.05, letter, transform=ax.transAxes, fontsize=14, fontweight='bold', va='top')

axes[0].set_yticks([0, 288, 1333])
axes[1].set_yticks([285, 288, 291])
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, bbox_to_anchor=(0.7, 0), ncol=2, frameon=False)
fig.savefig("plots/diurnal_cycle_radiation.pdf", bbox_inches='tight')
# %%
