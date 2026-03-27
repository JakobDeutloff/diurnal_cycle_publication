# %%
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from src.read_data import read_snapshot_data
# %%
bts, iwp = read_snapshot_data()

# %% plot bt and iwp snapshots
fig, axes = plt.subplots(1, 2, figsize=(10, 6), sharex=True, sharey=True)
iwp_cmap = LinearSegmentedColormap.from_list("iwp_cmap", ["#000000", "#fcfcfc"])
lat_range = slice(-5, 1)
lon_range = slice(22, 29)
axes[1].set_facecolor("#000000")

im0 = axes[0].pcolormesh(
    bts["lon"].sel(lon=lon_range),
    bts["lat"].sel(lat=lat_range),
    bts["Tb"].sel(lat=lat_range, lon=lon_range).isel(time=0),
    cmap="inferno",
    rasterized=True,
    vmin=200,
    vmax=290,
)
ct0 = axes[0].contour(
    bts["lon"].sel(lon=lon_range),
    bts["lat"].sel(lat=lat_range),
    bts["Tb"].sel(lat=lat_range, lon=lon_range).isel(time=0),
    levels=[231, 261],
    colors="white",
    linewidths=2,
    linestyles=["solid", "dotted"],
)
im1 = axes[1].pcolormesh(
    iwp["longitude"].sel(longitude=lon_range),
    iwp["latitude"].sel(latitude=lat_range),
    iwp.sel(latitude=lat_range, longitude=lon_range).isel(time=0),
    cmap=iwp_cmap,
    norm=LogNorm(1e-3, 1e1),
    rasterized=True,
)
ct1 = axes[1].contour(
    iwp["longitude"].sel(longitude=lon_range),
    iwp["latitude"].sel(latitude=lat_range),
    iwp.sel(latitude=lat_range, longitude=lon_range).isel(time=0),
    levels=[1e-1, 1],
    colors="black",
    linewidths=2,
    linestyles=["dotted", "solid"],
)
for ax in axes:
    ax.set_xlabel("Longitude / °E")
    ax.spines[["top", "right"]].set_visible(False)
axes[0].set_ylabel("Latitude / °N")

# make legends
leg = axes[0].legend(
    [
        plt.Line2D([], [], color="white", linestyle=":"),
        plt.Line2D([], [], color="white", linestyle="-"),
    ],
    ["$T_{b} = 261$ K", "$T_{b} = 231$ K"],
    loc="upper right",
    facecolor="black",
    edgecolor="black",
)
for text in leg.get_texts():
    text.set_color("white")

leg = axes[1].legend(
    [
        plt.Line2D([], [], color="black", linestyle=":"),
        plt.Line2D([], [], color="black", linestyle="-"),
    ],
    ["$I$ = 0.1 kg m$^{-2}$", "$I$ = 1 kg m$^{-2}$"],
    loc="upper right",
    facecolor="white",
    edgecolor="black",
)

fig.colorbar(
    im0,
    ax=axes[0],
    label="$T_{b}$ / K",
    orientation="horizontal",
    extend="both",
    pad=0.1,
)
fig.colorbar(
    im1,
    ax=axes[1],
    label="$I$ / kg m$^{-2}$",
    orientation="horizontal",
    extend="both",
    pad=0.1,
)
# add letter 
for ax, letter, color in zip(axes, ["a", "b"], ['black', 'white']):
    ax.text(
        0.02,
        0.93,
        letter,
        transform=ax.transAxes,
        fontsize=22,
        fontweight="bold",
        color=color,
    )
fig.tight_layout()
fig.savefig("plots/bt_iwp_snapshot.pdf")

# %%
