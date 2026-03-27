import numpy as np
import xarray as xr
from scipy.signal import detrend
import pandas as pd
from scipy.stats import linregress


def nan_detrend(da, dim="iwp"):
    out = xr.zeros_like(da)
    for i in da[dim]:
        y = da.sel({dim: i}).values
        mask = np.isfinite(y)
        if np.sum(mask) > 1:
            x = np.arange(len(y))
            # fit linear trend
            slope, intercept = np.polyfit(x[mask], y[mask], 1)
            trend = slope * x + intercept
            out.loc[{dim: i}] = y - trend
    return out


def deseason(ts):
    ts_deseason = ts.groupby("time.month") - ts.groupby("time.month").mean("time")
    ts_deseason["time"] = pd.to_datetime(ts_deseason["time"].dt.strftime("%Y-%m"))
    return ts_deseason


def regress_hist_temp_1d(cf_detrend, temp, cf):
    slopes = []
    err = []
    cf_dummy = cf_detrend.where(cf_detrend.notnull(), drop=True)
    temp_vals = temp.sel(time=cf_dummy.time).values
    for i in range(cf_dummy.local_time.size):
        cf_vals = cf_dummy.isel(local_time=i).values
        slope, intercept, r_value, p_value, std_err = linregress(temp_vals, cf_vals)
        slopes.append(slope)
        err.append(std_err)
    slopes_da = xr.DataArray(
        slopes,
        coords={"local_time": cf_dummy.local_time},
        dims=["local_time"],
    )
    err_da = xr.DataArray(
        err,
        coords={"local_time": cf_dummy.local_time},
        dims=["local_time"],
    )
    mean_cf = cf.mean("time")
    slopes_perc = slopes_da * 100 / mean_cf
    err_perc = err_da * 100 / mean_cf
    return slopes_perc, err_perc


def detrend_hist_2d(hist):

    out = xr.zeros_like(hist)
    if "bt" in hist.dims:
        detrend_dim = "bt"
    else:
        detrend_dim = "iwp"
    for i in hist[detrend_dim]:
        hist_detrend = nan_detrend(hist.sel({detrend_dim: i}), dim="local_time")
        out.loc[{detrend_dim: i}] = hist_detrend
    return out


def regress_hist_temp_2d(cf_detrend, temp, cf):
    if "bt" in cf_detrend.dims:
        detrend_dim = "bt"
    else:
        detrend_dim = "iwp"

    slopes = xr.zeros_like(cf_detrend.isel(time=0))
    p_values = xr.zeros_like(cf_detrend.isel(time=0))
    for i in cf_detrend.local_time:
        for j in cf_detrend[detrend_dim]:
            cf_vals = cf_detrend.sel({"local_time": i, detrend_dim: j})
            cf_vals = cf_vals.where(np.isfinite(cf_vals), drop=True)
            temp_vals = temp.sel(time=cf_vals.time)
            slope, intercept, r_value, p_value, std_err = linregress(
                temp_vals.values, cf_vals.values
            )
            slopes.loc[{"local_time": i, detrend_dim: j}] = slope
            p_values.loc[{"local_time": i, detrend_dim: j}] = p_value

    mean_hist = cf.mean("time")
    slopes_perc = slopes * 100 / mean_hist
    return slopes_perc, p_values



