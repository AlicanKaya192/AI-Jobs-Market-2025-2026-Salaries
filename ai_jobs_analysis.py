import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from scipy import stats
from collections import Counter
import warnings

# Suppress annoying runtime warnings (e.g., from matplotlib styles or pandas operations)
warnings.filterwarnings('ignore')

# Create the directory to store the output visualization charts if it doesn't already exist
os.makedirs('results', exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL GRAPH CONFIGURATION (MATPLOTLIB AESTHETICS)
# ═══════════════════════════════════════════════════════════════════════════
# We define a sleek, modern, minimalist styling system with warm off-white backgrounds,
# removing top/right axes lines (spines), and defining soft gridlines for visual comfort.
plt.rcParams.update({
    'font.family':       'DejaVu Sans',    # Standard clean font supported across operating systems
    'axes.spines.top':   False,            # Hide top boundary line of plots
    'axes.spines.right': False,            # Hide right boundary line of plots
    'figure.facecolor':  '#FAFAF8',        # Soft off-white background for the overall figure canvas
    'axes.facecolor':    '#FAFAF8',        # Match plot area background with the figure canvas background
    'axes.grid':         True,             # Enable grid lines by default to aid value estimation
    'grid.color':        '#E8E8E3',        # Soft, non-intrusive gray-brown color for grid lines
    'grid.linewidth':    0.6,              # Thin grid lines
    'axes.labelcolor':   '#333333',        # Dark gray for labels (better readability than pure black)
    'xtick.color':       '#555555',        # Slightly lighter gray for X-axis ticks
    'ytick.color':       '#555555',        # Slightly lighter gray for Y-axis ticks
    'text.color':        '#222222',        # Very dark gray for all text annotations
})

# A curated categorical color palette used consistently across all visualizations
PALETTE = [
    '#1976D2',  # Classic Blue
    '#388E3C',  # Emerald Green
    '#F57C00',  # Warm Amber
    '#7B1FA2',  # Deep Purple
    '#E64A19',  # Deep Rust/Orange
    '#00796B',  # Dark Teal
    '#C62828',  # Crimson Red
    '#0288D1',  # Light Blue
    '#558B2F',  # Olive Green
    '#6A1B9A',  # Violet Purple
    '#EF6C00',  # Orange-Yellow
    '#00695C'   # Forest Teal
]

# ═══════════════════════════════════════════════════════════════════════════
# DATA LOADING & ROBUST FILE PATH RESOLUTION
# ═══════════════════════════════════════════════════════════════════════════
# To make this script robust and runnable across local systems, cloud servers, and
# Kaggle notebooks, we search through multiple potential locations for the CSV dataset.
potential_paths = [
    'dataset/ai_jobs_market_2025_2026.csv',                                        # Local relative directory path
    'ai_jobs_market_2025_2026.csv',                                                # Current root directory
    '/mnt/user-data/uploads/ai_jobs_market_2025_2026.csv',                         # Original server path
    '/kaggle/input/ai-jobs-market-2025-2026-salaries/ai_jobs_market_2025_2026.csv', # Standard Kaggle input path
    '../input/ai-jobs-market-2025-2026-salaries/ai_jobs_market_2025_2026.csv'      # Alternative Kaggle folder
]

dataset_path = None
for path in potential_paths:
    if os.path.exists(path):
        dataset_path = path
        break

# Fallback in case none exist (falls back to local relative path)
if dataset_path is None:
    dataset_path = 'dataset/ai_jobs_market_2025_2026.csv'

# Read the comma-separated values (CSV) file into a Pandas DataFrame
df = pd.read_csv(dataset_path)
print(f"Loaded {len(df)} rows from: {dataset_path}")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 1 — Top 15 Job Titles by Median Salary + Demand Score
# ═══════════════════════════════════════════════════════════════════════════
# Objective: Identify the most lucrative AI job roles and correlate their pay
# with their respective industry demand scores.
#
# Process:
# 1. Group by 'job_title' and aggregate: median salary, mean demand score, and count of job postings.
# 2. Sort by 'median_salary' in descending order and select the top 15 records.
title_stats = (df.groupby('job_title')
                 .agg(median_salary=('annual_salary_usd','median'),
                      demand=('demand_score','mean'),
                      count=('job_id','count'))
                 .reset_index()
                 .sort_values('median_salary', ascending=False)
                 .head(15))

# Initialize a custom figure canvas
fig, ax = plt.subplots(figsize=(13, 8))
fig.patch.set_facecolor('#FAFAF8')
ax.set_facecolor('#FAFAF8')

# Dynamically assign colors from the palette to each bar, cycling if titles exceed palette size
colors = [PALETTE[i % len(PALETTE)] for i in range(len(title_stats))]

# Plot horizontal bars. [::-1] is used to reverse the order so the highest salary is at the top of the chart.
# Salary values are divided by 1000 to convert raw USD to thousands ($k) for a cleaner axis.
bars = ax.barh(title_stats['job_title'][::-1],
               title_stats['median_salary'][::-1] / 1000,
               color=colors[::-1], alpha=0.88,
               edgecolor='white', linewidth=0.8)

# Add custom textual annotations indicating the median salary ($k) and demand score right next to each bar
for bar, (_, row) in zip(bars, title_stats[::-1].iterrows()):
    ax.text(bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            f'${row["median_salary"]/1000:.0f}k  |  demand: {row["demand"]:.0f}/100',
            va='center', fontsize=8.5, color='#333', fontweight='bold')

# Configure labels, limits, tick formatting, and title
ax.set_xlabel('Median Annual Salary (USD thousands)', fontsize=11)
ax.set_title('Highest Paying AI Job Titles in 2025–2026\nMedian Salary + Demand Score',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(0, 420) # Limit X-axis to provide enough whitespace for annotations
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}k'))

# Bottom source tag annotation
ax.text(0.01, -0.06,
        f'Source: AI Jobs Market 2025–2026 Dataset (Kaggle) | n={len(df)} job postings',
        transform=ax.transAxes, fontsize=7.5, color='#888', style='italic')

# Adjust layout to fit everything and save the figure
plt.tight_layout()
plt.savefig('results/ai_top_paying_job_titles.png', dpi=180,
            bbox_inches='tight', facecolor='#FAFAF8')
plt.close()
print("Chart 1 done -> ai_top_paying_job_titles.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 2 — Salary by Experience Level (Box Plot with Jittered Scatter Overlay)
# ═══════════════════════════════════════════════════════════════════════════
# Objective: Visualize how salary scales across different career stages and measure
# the exact financial step-ups (deltas) between experience levels.
#
# Process:
# 1. Define explicit experience order from Entry to Lead.
# 2. Extract salary arrays corresponding to each experience level.
# 3. Create a box plot displaying medians and quartiles.
# 4. Overlay jittered points (random horizontal displacement) to show the underlying data density.
# 5. Add connection annotations indicating the increase in median salary between stages.
exp_order = ['Entry (0-2 yrs)', 'Mid (3-5 yrs)', 'Senior (6-9 yrs)', 'Lead (10+ yrs)']
exp_data  = [df[df['experience_level'] == e]['annual_salary_usd'].values for e in exp_order]
exp_colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0']  # Visual encoding: Green, Blue, Orange, Purple
exp_labels = ['Entry\n(0–2 yrs)', 'Mid\n(3–5 yrs)', 'Senior\n(6–9 yrs)', 'Lead\n(10+ yrs)']

fig, ax = plt.subplots(figsize=(11, 7))
fig.patch.set_facecolor('#FAFAF8')
ax.set_facecolor('#FAFAF8')

# Render the standard boxes representing interquartile range (IQR) and median lines
bp = ax.boxplot(exp_data, patch_artist=True,
                medianprops=dict(color='white', linewidth=2.5),
                whiskerprops=dict(linewidth=1.3),
                capprops=dict(linewidth=1.3),
                flierprops=dict(marker='o', markersize=3.5, alpha=0.4))

# Fill boxes with custom distinct colors
for patch, col in zip(bp['boxes'], exp_colors):
    patch.set_facecolor(col)
    patch.set_alpha(0.80)

# Overlay individual data points (scatter dots) with random horizontal jitter.
# This reveals data concentration and sample density which standard box plots mask.
for i, (data, col) in enumerate(zip(exp_data, exp_colors), 1):
    # np.random.normal generates horizontal offsets around the discrete box index i
    x = np.random.normal(i, 0.07, size=len(data))
    ax.scatter(x, data / 1000, alpha=0.25, color=col, s=18, zorder=3)

# Place numeric median salary text flags directly above each median line
for i, data in enumerate(exp_data, 1):
    med = np.median(data) / 1000
    ax.text(i, med + 5, f'${med:.0f}k', ha='center',
            fontsize=10, fontweight='bold', color='#333')

# Format axes and labels
ax.set_xticklabels(exp_labels, fontsize=11)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}k'))
ax.set_ylabel('Annual Salary (USD)', fontsize=11)
ax.set_title('How Much Does Experience Add to Your AI Salary?\nSalary Distribution by Experience Level',
             fontsize=14, fontweight='bold', pad=15)

# Calculate and draw step-up salary badges between consecutive experience classes
medians = [np.median(d) / 1000 for d in exp_data]
for i in range(1, len(medians)):
    delta = medians[i] - medians[i-1]
    ax.annotate(f'+${delta:.0f}k',
                xy=(i + 0.5, (medians[i] + medians[i-1]) / 2),
                fontsize=9.5, color='#388E3C', fontweight='bold', ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#E8F5E9', edgecolor='#388E3C', lw=0.8))

# Source caption
ax.text(0.01, -0.07,
        'Source: AI Jobs Market 2025–2026 Dataset (Kaggle) | Each dot = one job posting',
        transform=ax.transAxes, fontsize=7.5, color='#888', style='italic')

plt.tight_layout()
plt.savefig('results/ai_salary_by_experience.png', dpi=180,
            bbox_inches='tight', facecolor='#FAFAF8')
plt.close()
print("Chart 2 done -> ai_salary_by_experience.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 3 — Salary by Country (Top Countries)
# ═══════════════════════════════════════════════════════════════════════════
# Objective: Explore geographic differences in AI compensation and identify where
# the highest-earning hotspots are located.
#
# Process:
# 1. Filter out general "Global" roles to focus on physical countries.
# 2. Group by 'country' and calculate median salary, mean salary, and posting counts.
# 3. Sort by median salary descending.
# 4. Draw bars representing medians and overlay diamond points indicating mean salaries.
country_stats = (df[df['country'] != 'Global']
                   .groupby('country')
                   .agg(median_sal=('annual_salary_usd','median'),
                        mean_sal=('annual_salary_usd','mean'),
                        count=('job_id','count'))
                   .reset_index()
                   .sort_values('median_sal', ascending=False))

fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor('#FAFAF8')
ax.set_facecolor('#FAFAF8')

# Dynamic colors for the columns
colors_c = [PALETTE[i % len(PALETTE)] for i in range(len(country_stats))]
bars = ax.bar(country_stats['country'],
              country_stats['median_sal'] / 1000,
              color=colors_c, alpha=0.88,
              edgecolor='white', linewidth=0.8)

# Overlay Mean salary diamonds (compares skewness - if mean > median, indicates high-income outliers)
ax.scatter(range(len(country_stats)),
           country_stats['mean_sal'] / 1000,
           color='#333', s=55, zorder=5, label='Mean salary', marker='D')

# Label bar tops with median value and job posting sample size (n), positioned above both median and mean to avoid overlap
for bar, (_, row) in zip(bars, country_stats.iterrows()):
    y_pos = max(row["median_sal"], row["mean_sal"]) / 1000 + 4.5
    ax.text(bar.get_x() + bar.get_width() / 2,
            y_pos,
            f'${row["median_sal"]/1000:.0f}k\nn={int(row["count"])}',
            ha='center', va='bottom', fontsize=8, fontweight='bold', color='#333')

# Format axes and titles
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}k'))
ax.set_xlabel('Country', fontsize=11)
ax.set_ylabel('Median Annual Salary (USD)', fontsize=11)
ax.set_title('Where Do AI Professionals Earn the Most?\nMedian Salary by Country (2025–2026)',
             fontsize=14, fontweight='bold', pad=15)
ax.legend(fontsize=9, framealpha=0.9)

# Source caption
ax.text(0.01, -0.09,
        'Source: AI Jobs Market 2025–2026 Dataset (Kaggle) | "Global" remote roles excluded',
        transform=ax.transAxes, fontsize=7.5, color='#888', style='italic')

plt.tight_layout()
plt.savefig('results/ai_salary_by_country.png', dpi=180,
            bbox_inches='tight', facecolor='#FAFAF8')
plt.close()
print("Chart 3 done -> ai_salary_by_country.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 4 — Remote vs On-site vs Hybrid Salary Comparison (Histograms)
# ═══════════════════════════════════════════════════════════════════════════
# Objective: Investigate whether remote working agreements lead to lower, equal,
# or higher salaries than on-site or hybrid roles.
#
# Process:
# 1. Separate salaries according to 'On-site', 'Hybrid', and 'Fully Remote'.
# 2. Build a 1-row, 3-column histogram plot panel sharing the same Y-axis for easy comparison.
# 3. For each group, show frequency distribution and draw vertical lines for median (dashed) and mean (dotted).
remote_order  = ['On-site', 'Hybrid', 'Fully Remote']
remote_colors = ['#F44336', '#FF9800', '#4CAF50']  # Red, Orange, Green representing structural options
remote_data   = [df[df['remote_work'] == r]['annual_salary_usd'].values for r in remote_order]

fig, axes = plt.subplots(1, 3, figsize=(14, 6), sharey=True)
fig.patch.set_facecolor('#FAFAF8')

for ax, rtype, col, data in zip(axes, remote_order, remote_colors, remote_data):
    ax.set_facecolor('#FAFAF8')
    # Render histograms showing frequency counts of salaries
    ax.hist(data / 1000, bins=20, color=col, alpha=0.78,
            edgecolor='white', linewidth=0.5)
    
    med = np.median(data) / 1000
    mn  = np.mean(data) / 1000
    
    # Draw reference line for median (dashed)
    ax.axvline(med, color='#333', linewidth=2, linestyle='--', label=f'Median: ${med:.0f}k')
    # Draw reference line for mean (dotted)
    ax.axvline(mn,  color='#999', linewidth=1.5, linestyle=':',  label=f'Mean: ${mn:.0f}k')
    
    # Label panel
    ax.set_title(rtype, fontsize=13, fontweight='bold', color=col, pad=10)
    ax.set_xlabel('Annual Salary (USD)', fontsize=10)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}k'))
    ax.legend(fontsize=8.5, framealpha=0.9)
    
    # Subtext displaying sample sizes and medians per subplot
    ax.text(0.5, -0.14, f'n = {len(data)}  |  Median ${med:.0f}k',
            transform=ax.transAxes, ha='center',
            fontsize=9, fontweight='bold', color='#555')

axes[0].set_ylabel('Number of Job Postings', fontsize=11)
fig.suptitle('Does Remote Work Pay More?\nSalary Distribution by Work Arrangement (2025–2026)',
             fontsize=14, fontweight='bold', y=1.02)

# Figure source tag
fig.text(0.5, -0.06,
         'Source: AI Jobs Market 2025–2026 Dataset (Kaggle)',
         ha='center', fontsize=7.5, color='#888', style='italic')

plt.tight_layout()
plt.savefig('results/ai_salary_remote_vs_onsite.png', dpi=180,
            bbox_inches='tight', facecolor='#FAFAF8')
plt.close()
print("Chart 4 done -> ai_salary_remote_vs_onsite.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 5 — Top 25 Most In-Demand Skills matched with their Median Salary
# ═══════════════════════════════════════════════════════════════════════════
# Objective: Uncover which programming languages, frameworks, or methodologies
# are most frequent in job postings, and map their salary value.
#
# Process:
# 1. Parse individual skill tags from 'required_skills' (delimited by '|').
# 2. Count absolute frequency of occurrences using a Counter.
# 3. Pull the top 25 skills.
# 4. Map the median salary of job roles containing each target skill.
# 5. Represent counts as horizontal bars and map salaries as colors using a color scale (heatmap colorbar).
all_skills = []
for skills_str in df['required_skills']:
    # Tokenize the pipe-delimited skills string and remove blank margins
    all_skills.extend([s.strip() for s in skills_str.split('|')])

skill_counts = Counter(all_skills)
top_skills   = pd.DataFrame(skill_counts.most_common(25),
                             columns=['skill', 'count'])

# Query median salary of jobs that list the specified skill in their required skills
skill_salaries = {}
for skill in top_skills['skill']:
    # Filter using regex=False for simple substring matching (faster and safer)
    mask = df['required_skills'].str.contains(skill, regex=False)
    skill_salaries[skill] = df[mask]['annual_salary_usd'].median() / 1000
top_skills['median_salary_k'] = top_skills['skill'].map(skill_salaries)

# Sort from lowest count to highest count for display order (ascending barh)
top_skills = top_skills.sort_values('count', ascending=True)

fig, ax = plt.subplots(figsize=(13, 10))
fig.patch.set_facecolor('#FAFAF8')
ax.set_facecolor('#FAFAF8')

# Color mapping logic: normalize median salary limits, map to Red-Yellow-Green colormap (RdYlGn)
# Green = highly compensated skills, Red = lower relative compensation skills.
norm = plt.Normalize(top_skills['median_salary_k'].min(),
                     top_skills['median_salary_k'].max())
cmap = plt.cm.RdYlGn
colors_skill = cmap(norm(top_skills['median_salary_k'].values))

# Render horizontal bar chart
bars = ax.barh(top_skills['skill'], top_skills['count'],
               color=colors_skill, alpha=0.90,
               edgecolor='white', linewidth=0.6)

# Display exact counts and median salary levels next to each bar
for bar, (_, row) in zip(bars, top_skills.iterrows()):
    ax.text(bar.get_width() + 2,
            bar.get_y() + bar.get_height() / 2,
            f"{int(row['count'])}  |  ${row['median_salary_k']:.0f}k",
            va='center', fontsize=8.5, color='#333', fontweight='bold')

# Configure the Colorbar (Visual salary scale indicator)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, shrink=0.6, pad=0.01)
cbar.set_label('Median Salary of Roles\nRequiring This Skill ($k)', fontsize=9)

# Labels and margins
ax.set_xlabel('Number of Job Postings', fontsize=11)
ax.set_title('Top 25 Most In-Demand AI Skills (2025–2026)\nColour = Median Salary of Roles Requiring That Skill',
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlim(0, top_skills['count'].max() * 1.25)

# Source caption
ax.text(0.01, -0.05,
        'Source: AI Jobs Market 2025–2026 Dataset (Kaggle)',
        transform=ax.transAxes, fontsize=7.5, color='#888', style='italic')

plt.tight_layout()
plt.savefig('results/ai_top_skills_demand_salary.png', dpi=180,
            bbox_inches='tight', facecolor='#FAFAF8')
plt.close()
print("Chart 5 done -> ai_top_skills_demand_salary.png")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 6 — LLM Roles vs Non-LLM Roles: Premium, Demand, Growth, & Benefits
# ═══════════════════════════════════════════════════════════════════════════
# Objective: Measure the direct economic premium of LLM (Large Language Model)
# roles compared to traditional AI positions across multiple vectors.
#
# Process:
# 1. Segment dataset into LLM roles (is_llm_role = 1) and Non-LLM roles (is_llm_role = 0).
# 2. Compile metrics (median salary, mean premium pct, mean demand, YoY demand growth, benefits score).
# 3. Create a 5-panel subplot array.
# 4. Render side-by-side comparison bars for each metric and annotate differences.
llm     = df[df['is_llm_role'] == 1]
non_llm = df[df['is_llm_role'] == 0]

metrics = {
    'Median Salary ($k)':         [llm['annual_salary_usd'].median()/1000,
                                   non_llm['annual_salary_usd'].median()/1000],
    'AI Salary Premium (%)':      [llm['ai_salary_premium_pct'].mean(),
                                   non_llm['ai_salary_premium_pct'].mean()],
    'Demand Score (/100)':        [llm['demand_score'].mean(),
                                   non_llm['demand_score'].mean()],
    'YoY Demand Growth (%)':      [llm['demand_growth_yoy_pct'].mean(),
                                   non_llm['demand_growth_yoy_pct'].mean()],
    'Benefits Score (/10)':       [llm['benefits_score_10'].mean(),
                                   non_llm['benefits_score_10'].mean()],
}

fig, axes = plt.subplots(1, 5, figsize=(17, 6))
fig.patch.set_facecolor('#FAFAF8')

for ax, (metric, (llm_val, non_val)) in zip(axes, metrics.items()):
    ax.set_facecolor('#FAFAF8')
    # Render two side-by-side columns: Purple for LLM, Blue for Non-LLM
    bars = ax.bar(['LLM\nRoles', 'Non-LLM\nRoles'],
                  [llm_val, non_val],
                  color=['#7B1FA2', '#1976D2'], alpha=0.85,
                  edgecolor='white', linewidth=0.8,
                  width=0.5)
    
    # Annotate absolute value numbers above columns
    for bar, val in zip(bars, [llm_val, non_val]):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + max(llm_val, non_val) * 0.02,
                f'{val:.1f}', ha='center', fontsize=10,
                fontweight='bold', color='#333')
        
    # Calculate premium delta & percentage ratio relative to non-LLM baselines
    delta = llm_val - non_val
    pct   = (delta / non_val) * 100
    sign  = '+' if delta > 0 else ''
    
    # Subtitle for metric details
    ax.set_title(metric, fontsize=9.5, fontweight='bold', pad=8)
    
    # Bottom text badge showing the percentage advantage of LLM roles
    ax.text(0.5, -0.18, f'LLM premium: {sign}{pct:.1f}%',
            transform=ax.transAxes, ha='center',
            fontsize=8.5, color='#7B1FA2' if delta > 0 else '#E53935',
            fontweight='bold')
    
    ax.tick_params(axis='x', labelsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', color='#E8E8E3', linewidth=0.6)

# Construct figure legend representing the two cohorts
llm_patch     = mpatches.Patch(color='#7B1FA2', alpha=0.85, label=f'LLM Roles (n={len(llm)})')
non_llm_patch = mpatches.Patch(color='#1976D2', alpha=0.85, label=f'Non-LLM Roles (n={len(non_llm)})')
fig.legend(handles=[llm_patch, non_llm_patch], loc='lower center',
           ncol=2, fontsize=10, bbox_to_anchor=(0.5, -0.08), framealpha=0.9)

fig.suptitle('LLM Roles vs. Everything Else: Are They Worth the Hype?\nKey Metrics Comparison — AI Jobs 2025–2026',
             fontsize=14, fontweight='bold', y=1.04)

# Source caption
fig.text(0.5, -0.13,
         'Source: AI Jobs Market 2025–2026 Dataset (Kaggle)',
         ha='center', fontsize=7.5, color='#888', style='italic')

plt.tight_layout()
plt.savefig('results/ai_llm_vs_nonllm_comparison.png', dpi=180,
            bbox_inches='tight', facecolor='#FAFAF8')
plt.close()
print("Chart 6 done -> ai_llm_vs_nonllm_comparison.png")

print("\nAll 6 charts saved to results/")