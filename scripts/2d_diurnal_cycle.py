# %%
import xarray as xr
from src.helper_functions import (
    deseason,
    detrend_hist_2d,
    regress_hist_temp_2d,
)
from src.read_data import (
    read_ccic_histograms,
    read_temperature,
    read_albedo,
    read_sw_in,
    read_feedback_bs,
)
from src.plot import plot_2d_trend
from scipy.signal import detrend


# %% load ccic data, temperature and bootstrapped feedbacks
hist = read_ccic_histograms("all")
temp = read_temperature("all")
albedo = read_albedo()
SW_in = read_sw_in()
feedback_bs = read_feedback_bs()
SW_in = SW_in.interp(time_points=hist["local_time"], method="linear")

# %% calculate cloud fraction
cf = hist["hist"] / hist["hist"].sum(["local_time", "iwp"])

# %% normalise cloud fraction
cf_norm = cf / cf.sum("local_time")

# %%  detrend and deseasonalize
temp_detrend = xr.DataArray(detrend(temp), coords=temp.coords, dims=temp.dims)
temp_detrend = deseason(temp_detrend)
cf_detrend = detrend_hist_2d(cf_norm)
cf_detrend = deseason(cf_detrend)

# %% regression
slope, p_value = regress_hist_temp_2d(cf_detrend, temp_detrend, cf_norm)

# %% calculate feedback
cf_change = (slope / 100) * cf.mean("time")  # 1/K
feedback = -1 * (
    (cf_change * SW_in * albedo['hc_albedo'].values.T) - ((cf_change) * SW_in * 0.1)
)  # W / m^2 / K
feedbacks_int = feedback.sel(iwp=slice(1e-1, None)).sum()  # W / m^2 / K

# %% calculate cumulative feedback from bootstrapped samples
feedback_cum_bs = (
    feedback_bs
    .sel(iwp=slice(1e-1, None))
    .sum("local_time")
    .cumsum("iwp")
    .mean(dim="iteration")
)
err_feedback_bs = (
    feedback_bs
    .sel(iwp=slice(1e-1, None))
    .sum("local_time")
    .cumsum("iwp")
    .std(dim="iteration")
)

# %% plot slopes ccic
fig, axes = plot_2d_trend(
    cf.mean("time"),
    slope - slope.mean("local_time"),
    cf_change,
    feedback,
    p_value,
    feedback_cum_bs,
    err_feedback_bs,
    dim="iwp",
)
fig.savefig("plots/ccic_2d_trend.pdf", bbox_inches='tight')

# %%
