"""
Statistical Analysis Script — Jaundice Detection Pipeline
==========================================================
Professor Ian's feedback:
  - Calculate mean colour for pre and post processed images (in Lab colourspace)
  - Run paired t-test to see if the two groups are significantly different
  - If distributions not normal → fallback to Mann-Whitney U test
  - Can do per channel (L*, a*, b*), greyscale (L* only), or combined metric (ΔE)
  - p < 0.05 → groups are significantly different

USAGE:
  python statistical_analysis.py --file metadata.xlsx

WHAT YOUR metadata.xlsx NEEDS:
  Current columns (post only):
    mean_L, mean_a, mean_b, std_L, std_a, std_b, cv_b, ssim

  You need to ADD these columns in your Flask pipeline (save_metadata):
    pre_mean_L, pre_mean_a, pre_mean_b
    pre_std_L,  pre_std_a,  pre_std_b

  See bottom of this file for how to add that in Flask.

Author: Generated for Karan's FYP — ARU
"""

import argparse
import sys
import os
import numpy as np
import pandas as pd
from scipy import stats  # for t-tests and shapiro-wilk normality test
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")  # suppress annoying warnings during stats


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def check_normality(data, name, alpha=0.05):
    """Shapiro-Wilk normality test. Returns (is_normal, p_value)."""
    if len(data) < 3:
        # can't run a proper test with fewer than 3 samples
        print(f"  [WARN] {name}: only {len(data)} samples — need ≥3 for normality test.")
        return False, None
    stat, p = stats.shapiro(data)
    is_normal = p > alpha
    symbol = "✓ NORMAL" if is_normal else "✗ NOT NORMAL"
    print(f"  Shapiro-Wilk {name}: W={stat:.4f}, p={p:.4f}  → {symbol}")
    return is_normal, p


def run_paired_ttest(pre, post, channel_name):
    """Paired t-test between pre and post arrays."""
    t_stat, p_val = stats.ttest_rel(pre, post)  # paired = same images, before and after
    sig = "SIGNIFICANT (p < 0.05)" if p_val < 0.05 else "not significant (p ≥ 0.05)"
    print(f"  Paired t-test  {channel_name}: t={t_stat:.4f}, p={p_val:.4f}  → {sig}")
    return t_stat, p_val


def run_mannwhitney(pre, post, channel_name):
    """Mann-Whitney U test (non-parametric fallback)."""
    u_stat, p_val = stats.mannwhitneyu(pre, post, alternative="two-sided")
    sig = "SIGNIFICANT (p < 0.05)" if p_val < 0.05 else "not significant (p ≥ 0.05)"
    print(f"  Mann-Whitney U {channel_name}: U={u_stat:.4f}, p={p_val:.4f}  → {sig}")
    return u_stat, p_val


def analyse_channel(pre_vals, post_vals, channel_name, alpha=0.05):
    """
    Full analysis for one channel:
      1. Normality check on both groups
      2. Paired t-test if both normal, else Mann-Whitney U
      3. Returns result dict
    """
    print(f"\n{'─'*55}")
    print(f"  Channel: {channel_name}")
    print(f"  n = {len(pre_vals)} image pairs")
    print(f"  Pre  — mean={np.mean(pre_vals):.4f}, std={np.std(pre_vals):.4f}")
    print(f"  Post — mean={np.mean(post_vals):.4f}, std={np.std(post_vals):.4f}")
    print(f"  Mean difference (post−pre) = {np.mean(post_vals - pre_vals):.4f}")

    pre_normal,  p_pre  = check_normality(pre_vals,  f"pre-{channel_name}")
    post_normal, p_post = check_normality(post_vals, f"post-{channel_name}")

    both_normal = pre_normal and post_normal
    test_used = "Paired t-test" if both_normal else "Mann-Whitney U"

    if both_normal:
        stat, p_val = run_paired_ttest(pre_vals, post_vals, channel_name)
    else:
        print(f"  → At least one group non-normal — falling back to Mann-Whitney U")
        stat, p_val = run_mannwhitney(pre_vals, post_vals, channel_name)

    significant = p_val < alpha

    return {
        "channel":       channel_name,
        "n":             len(pre_vals),
        "pre_mean":      round(float(np.mean(pre_vals)), 4),
        "post_mean":     round(float(np.mean(post_vals)), 4),
        "mean_diff":     round(float(np.mean(post_vals - pre_vals)), 4),
        "pre_normal":    pre_normal,
        "post_normal":   post_normal,
        "test_used":     test_used,
        "stat":          round(float(stat), 4),
        "p_value":       round(float(p_val), 4),
        "significant":   significant,
    }


def compute_delta_e(pre_L, pre_a, pre_b, post_L, post_a, post_b):
    """CIE76 ΔE between pre and post per image — single combined metric."""
    # delta E is basically the "total colour distance" between two colours
    # if delta E < 1, even a trained eye can't tell the difference!
    dL = post_L - pre_L
    da = post_a - pre_a
    db = post_b - pre_b
    return np.sqrt(dL**2 + da**2 + db**2)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

# Absolute path to the script's own directory — used for default paths
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_XLSX = os.path.join(_SCRIPT_DIR, "data", "results", "metadata.xlsx")


def main():
    parser = argparse.ArgumentParser(description="Paired t-test / Mann-Whitney U for pipeline pre vs post")
    parser.add_argument("--file", default=_DEFAULT_XLSX,
                        help="Path to metadata.xlsx (default: data/results/metadata.xlsx)")
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance threshold (default 0.05)")
    parser.add_argument("--plot", action="store_true",
                        help="Save distribution plots to data/results/stats_plots.png")
    args = parser.parse_args()

    # ── Load data ────────────────────────────────────────────
    print(f"\n{'═'*55}")
    print("  JAUNDICE PIPELINE — STATISTICAL ANALYSIS")
    print(f"  File:  {args.file}")
    print(f"  Alpha: {args.alpha}")
    print(f"{'═'*55}")

    try:
        df = pd.read_excel(args.file)
    except FileNotFoundError:
        print(f"\n[ERROR] File not found: {args.file}")
        sys.exit(1)

    print(f"\nLoaded {len(df)} rows, columns: {df.columns.tolist()}")

    # ── Check for pre columns ────────────────────────────────
    required_pre = ["pre_mean_L", "pre_mean_a", "pre_mean_b"]
    required_post = ["mean_L", "mean_a", "mean_b"]
    missing_pre = [c for c in required_pre if c not in df.columns]

    if missing_pre:
        print(f"\n[ERROR] Missing pre-processing columns: {missing_pre}")
        print("\nYour metadata.xlsx currently only has POST-processed values.")
        print("You need to add pre-processing colour values in your Flask save_metadata function.")
        print("\nSee the 'HOW TO ADD PRE VALUES IN FLASK' section at the bottom of this script.")
        print("\n── DEMO MODE ──────────────────────────────────────────")
        print("Running with SIMULATED pre-values (post + small noise) to show output format.")
        print("Replace with real data once you capture pre values.\n")

        # Simulate pre values for demo — slightly different from post
        np.random.seed(42)
        n = max(len(df), 15)  # pad with simulated rows if only 1 row
        if len(df) < 5:
            print(f"[NOTE] Only {len(df)} real row(s) — padding to {n} simulated rows for demo.")
            base_L = np.random.normal(df["mean_L"].mean(), 3, n)
            base_a = np.random.normal(df["mean_a"].mean(), 1, n)
            base_b = np.random.normal(df["mean_b"].mean(), 2, n)
        else:
            base_L = df["mean_L"].values
            base_a = df["mean_a"].values
            base_b = df["mean_b"].values

        pre_L = base_L + np.random.normal(0, 2, n)
        pre_a = base_a + np.random.normal(0, 0.5, n)
        pre_b = base_b + np.random.normal(0, 1.5, n)
        post_L = base_L
        post_a = base_a
        post_b = base_b
        demo_mode = True
    else:
        df = df.dropna(subset=required_pre + required_post)
        if len(df) < 3:
            print(f"[ERROR] Need at least 3 complete image pairs. Only {len(df)} found.")
            sys.exit(1)
        pre_L  = df["pre_mean_L"].values
        pre_a  = df["pre_mean_a"].values
        pre_b  = df["pre_mean_b"].values
        post_L = df["mean_L"].values
        post_a = df["mean_a"].values
        post_b = df["mean_b"].values
        demo_mode = False

    n = len(pre_L)

    # ── Run analysis per channel ─────────────────────────────
    print(f"\n{'═'*55}")
    print("  PER-CHANNEL ANALYSIS (CIE Lab)")
    results = []
    results.append(analyse_channel(pre_L, post_L, "L* (lightness)",  args.alpha))
    results.append(analyse_channel(pre_a, post_a, "a* (green-red)",  args.alpha))
    results.append(analyse_channel(pre_b, post_b, "b* (blue-yellow)", args.alpha))

    # ── Combined ΔE metric ───────────────────────────────────
    print(f"\n{'═'*55}")
    print("  COMBINED METRIC — CIE76 ΔE (pre vs post per image)")
    delta_e = compute_delta_e(pre_L, pre_a, pre_b, post_L, post_a, post_b)
    print(f"  ΔE values: mean={np.mean(delta_e):.4f}, std={np.std(delta_e):.4f}")
    print(f"  ΔE < 1 (imperceptible):  {(delta_e < 1).sum()}/{n} images")
    print(f"  ΔE 1–2 (just noticeable): {((delta_e >= 1) & (delta_e < 2)).sum()}/{n} images")
    print(f"  ΔE ≥ 2 (perceptible):    {(delta_e >= 2).sum()}/{n} images")

    # ── Greyscale (L* only) ──────────────────────────────────
    print(f"\n{'═'*55}")
    print("  GREYSCALE ANALYSIS (L* only)")
    results.append(analyse_channel(pre_L, post_L, "L* greyscale", args.alpha))

    # ── Summary table ────────────────────────────────────────
    print(f"\n{'═'*55}")
    print("  SUMMARY TABLE")
    print(f"{'═'*55}")
    print(f"  {'Channel':<20} {'Test':<18} {'stat':>8} {'p-value':>9} {'Sig?':>8}")
    print(f"  {'─'*20} {'─'*18} {'─'*8} {'─'*9} {'─'*8}")
    for r in results:
        sig_str = "YES ***" if r["significant"] else "no"
        print(f"  {r['channel']:<20} {r['test_used']:<18} {r['stat']:>8.4f} {r['p_value']:>9.4f} {sig_str:>8}")
    print(f"{'═'*55}")
    print(f"  Alpha = {args.alpha}  |  *** = p < {args.alpha}")
    if demo_mode:
        print("  [DEMO MODE — replace with real pre-processing data]")

    # ── Interpretation for report ────────────────────────────
    print(f"\n{'═'*55}")
    print("  INTERPRETATION (for Discussion section 6.1)")
    print(f"{'═'*55}")
    for r in results:
        ch = r["channel"]
        diff = r["mean_diff"]
        direction = "increased" if diff > 0 else "decreased"
        if r["significant"]:
            print(f"  {ch}: Pipeline caused a statistically significant {direction}")
            print(f"    (mean change = {diff:+.4f}, {r['test_used']}, p={r['p_value']:.4f})")
        else:
            print(f"  {ch}: No significant difference pre vs post")
            print(f"    (mean change = {diff:+.4f}, {r['test_used']}, p={r['p_value']:.4f})")
            print(f"    → Pipeline is colour-preserving for this channel ✓")

    # ── Optional plots ───────────────────────────────────────
    if args.plot:
        fig = plt.figure(figsize=(14, 10))
        fig.suptitle("Pre vs Post Processing — Colour Distribution Analysis", fontsize=14, fontweight="bold")
        gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

        channels = [
            ("L*", pre_L, post_L, "tab:blue"),
            ("a*", pre_a, post_a, "tab:green"),
            ("b*", pre_b, post_b, "tab:orange"),
        ]

        for idx, (ch_name, pre, post, colour) in enumerate(channels):
            ax = fig.add_subplot(gs[0, idx])
            ax.hist(pre, bins=15, alpha=0.6, label="Pre", color="grey")
            ax.hist(post, bins=15, alpha=0.6, label="Post", color=colour)
            ax.set_title(f"{ch_name} distribution")
            ax.set_xlabel("Value")
            ax.set_ylabel("Count")
            ax.legend(fontsize=8)

        # ΔE distribution
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.hist(delta_e, bins=15, color="tab:red", alpha=0.7)
        ax4.axvline(1.0, color="black", linestyle="--", linewidth=1, label="ΔE=1 (perceptible)")
        ax4.axvline(2.0, color="black", linestyle="-", linewidth=1, label="ΔE=2")
        ax4.set_title("CIE76 ΔE per image")
        ax4.set_xlabel("ΔE")
        ax4.set_ylabel("Count")
        ax4.legend(fontsize=8)

        # b* box plot (most important for jaundice)
        ax5 = fig.add_subplot(gs[1, 1])
        ax5.boxplot([pre_b, post_b], labels=["Pre b*", "Post b*"], patch_artist=True,
                    boxprops=dict(facecolor="tab:orange", alpha=0.5))
        ax5.set_title("b* boxplot (jaundice channel)")
        ax5.set_ylabel("b* value")

        # p-value summary bar
        ax6 = fig.add_subplot(gs[1, 2])
        labels = [r["channel"].split(" ")[0] for r in results[:3]]
        pvals  = [r["p_value"] for r in results[:3]]
        colours = ["tab:red" if p < args.alpha else "tab:green" for p in pvals]
        bars = ax6.bar(labels, pvals, color=colours, alpha=0.7)
        ax6.axhline(args.alpha, color="black", linestyle="--", linewidth=1, label=f"α={args.alpha}")
        ax6.set_title("p-values by channel")
        ax6.set_ylabel("p-value")
        ax6.legend(fontsize=8)
        for bar, pv in zip(bars, pvals):
            ax6.text(bar.get_x() + bar.get_width()/2, pv + 0.005, f"{pv:.3f}", ha="center", fontsize=9)

        out_dir   = os.path.join(_SCRIPT_DIR, "data", "results")
        os.makedirs(out_dir, exist_ok=True)
        plot_path = os.path.join(out_dir, "stats_plots.png")
        plt.savefig(plot_path, dpi=150, bbox_inches="tight")
        print(f"\n  Plots saved → {plot_path}")

    print()
    return results


# ─────────────────────────────────────────────────────────────
# HOW TO ADD PRE VALUES IN FLASK (add this to your pipeline)
# ─────────────────────────────────────────────────────────────
"""
In your Flask pipeline, BEFORE you run preprocessing/hair removal/skin mask,
extract Lab stats from the raw ROI crop and pass them to save_metadata.

Example (in your main pipeline function, e.g. process_image()):

    # --- After ROI selection, BEFORE processing ---
    roi_raw = lab_image[y:y+h, x:x+w]   # raw Lab ROI
    pre_stats = {
        "pre_mean_L": float(np.mean(roi_raw[:,:,0])),
        "pre_mean_a": float(np.mean(roi_raw[:,:,1])),
        "pre_mean_b": float(np.mean(roi_raw[:,:,2])),
        "pre_std_L":  float(np.std(roi_raw[:,:,0])),
        "pre_std_a":  float(np.std(roi_raw[:,:,1])),
        "pre_std_b":  float(np.std(roi_raw[:,:,2])),
    }

    # ... run your full pipeline (hair removal, skin mask, etc.) ...

    # --- Then merge pre_stats into your save_metadata call ---
    save_metadata({**post_stats, **pre_stats}, output_path)

Then in save_metadata / the xlsx writer, make sure these new columns
are written alongside the existing ones.
"""

if __name__ == "__main__":
    main()
