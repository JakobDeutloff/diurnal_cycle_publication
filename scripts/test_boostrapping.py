# %%
import matplotlib.pyplot as plt
import numpy as np
from src.read_data import read_bs_test

# %%
ds_size = read_bs_test()

# %%
n_iterations = sorted(ds_size.keys())
mean_feedback = np.zeros(len(n_iterations))
std_feedback = np.zeros(len(n_iterations))

for i, n in enumerate(n_iterations):
    mean_feedback[i] = ds_size[n].sum(['iwp', 'local_time']).mean('iteration').mean('repeat_iteration')
    std_feedback[i] = ds_size[n].sum(['iwp', 'local_time']).mean('iteration').std('repeat_iteration')
    

# %% 
fig, ax = plt.subplots(figsize=(6,4))
ax.plot(n_iterations, mean_feedback, marker='o', color='k', label='Mean')
ax.fill_between(n_iterations, mean_feedback - std_feedback, mean_feedback + std_feedback, alpha=0.3, color='gray', label=r'$\pm$  $\sigma$')
ax.set_xscale('log')
ax.set_xticks(n_iterations)
ax.set_xticklabels(n_iterations)
ax.spines[["top", "right"]].set_visible(False)
ax.set_xlabel("Sample Size")
ax.set_ylabel(r"$\lambda$ / W m$^{-2}$ K$^{-1}$")
ax.legend(frameon=False)
fig.savefig("plots/ccic_bootstrap_size_test.pdf", bbox_inches='tight')

# %%
