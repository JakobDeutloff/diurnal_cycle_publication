import xarray as xr
import pickle


def get_path():
    """
    Modify this function to return the path to the data directory on your system.

    return: str, path to the data directory
    """
    return "/work/bm1183/m301049/diurnal_cycle_publication/"


def read_ccic_histograms(name):
    """
    Read the CCIC histograms for the given name.
    name: str, one of "all", "sea", "land"
    return: xarray.Dataset, the CCIC histograms for the given name
    """
    path = get_path()
    return xr.open_dataset(f"{path}ccic_2d_monthly_{name}.nc")


def read_gpm_histograms(name):
    """
    Read the GPM histograms for the given name.
    name: str, one of "all", "sea", "land"
    return: xarray.Dataset, the GPM histograms for the given name
    """
    path = get_path()
    return xr.open_dataset(f"{path}gpm_2d_monthly_{name}.nc")


def read_temperature(name):
    """
    Read the temperature data for the given region.
    name: str, one of "all", "sea", "land"
    return: xarray.DataArray, the temperature data for the given region
    """
    path = get_path()
    return xr.open_dataset(f"{path}t2m_tropics_{name}.nc").t2m


def read_icon(name):
    """
    Read the ICON histograms for the given model run.
    name: str, one of "jed0011", "jed0022"
    return: xarray.DataArray, the ICON histograms for the given model run
    """
    path = get_path()
    return xr.open_dataset(f"{path}{name}_deep_clouds_daily_cycle.nc")[
        "__xarray_dataarray_variable__"
    ]

def read_albedo():
    """
    Read the albedo data.
    return: xarray.Dataset, the albedo data
    """
    path = get_path()
    return xr.open_dataset(f"{path}binned_hc_albedo_iwp.nc")

def read_sw_in():
    """
    Read the incoming shortwave radiation data.
    return: xarray.DataArray, the incoming shortwave radiation data
    """
    path = get_path()
    return xr.open_dataarray(f"{path}SW_in_daily_cycle.nc")

def read_lw_out():
    """
    Read the outgoing longwave radiation data.
    return: xarray.DataArray, the outgoing longwave radiation data
    """
    path = get_path()
    return xr.open_dataarray(f"{path}rlut_cs.nc")

def read_feedback_bs():
    """
    Read the bootstrapped feedback data.
    return: xarray.DataArray, the bootstrapped feedback data
    """
    path = get_path()
    return xr.open_dataarray(f"{path}ccic_bootstrap_feedback_2d.nc")

def read_bs_test():
    """
    Read the bootstrapped feedback data for the sample size.
    return: dict, the bootstrapped feedback data for the sample size tests
    """
    path = get_path()
    with open(f"{path}ccic_bootstrap_feedback_2d_sample_size_test.pkl", "rb") as f:
        ds_size = pickle.load(f)
    return ds_size

def read_snapshot_data():
    """
    Read the snapshot data for the brightness temperature and ice water path.
    return: tuple of xarray.Dataset, the brightness temperature and ice water path data
    """
    path = get_path()
    bts = (
        xr.open_mfdataset(
            f"{path}snapshot_data/merg_2008010901*.nc4", engine="netcdf4"
        )
        .sel(lat=slice(-30, 30))
        .load()
    )
    iwp = (
        xr.open_mfdataset(
            f"{path}snapshot_data/ccic_cpcir_2008010901*.zarr", engine="zarr"
        )
        .sel(latitude=slice(30, -30))
        .load()
    )["tiwp"]
    iwp = iwp[:, ::-1, :]
    iwp = iwp.fillna(0)
    return bts, iwp