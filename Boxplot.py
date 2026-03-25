from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "TgianPhanHoi_latency.xlsx"
OUTPUT_FILE = BASE_DIR / "boxplot_trong_nuoc_vs_quoc_te.png"


def load_data() -> pd.DataFrame:
	if not EXCEL_FILE.exists():
		raise FileNotFoundError(f"Khong tim thay file du lieu: {EXCEL_FILE}")

	df = pd.read_excel(EXCEL_FILE)
	required_columns = {"Loai_may_chu", "Do_tre_ms"}
	missing_columns = required_columns.difference(df.columns)
	if missing_columns:
		raise ValueError(
			"Thieu cot can thiet trong file Excel: " + ", ".join(sorted(missing_columns))
		)

	df = df[["Loai_may_chu", "Do_tre_ms"]].copy()
	df["Loai_may_chu"] = df["Loai_may_chu"].astype(str).str.strip()
	df["Do_tre_ms"] = pd.to_numeric(df["Do_tre_ms"], errors="coerce")
	df = df.dropna(subset=["Loai_may_chu", "Do_tre_ms"])

	group_order = ["Trong nuoc", "Quoc te"]
	df = df[df["Loai_may_chu"].isin(group_order)]
	df["Loai_may_chu"] = pd.Categorical(df["Loai_may_chu"], categories=group_order, ordered=True)

	if df.empty:
		raise ValueError("Khong co du lieu hop le de ve boxplot.")

	return df


def plot_boxplot(df: pd.DataFrame) -> None:
	plt.style.use("seaborn-v0_8-whitegrid")
	sns.set_context("notebook")

	fig, ax = plt.subplots(figsize=(11, 7))
	group_order = ["Trong nuoc", "Quoc te"]
	group_stats = (
		df.groupby("Loai_may_chu")["Do_tre_ms"]
		.agg(["count", "mean", "median", lambda s: s.quantile(0.75) - s.quantile(0.25)])
		.reindex(group_order)
	)
	group_stats.columns = ["count", "mean", "median", "iqr"]

	sns.boxplot(
		data=df,
		x="Loai_may_chu",
		y="Do_tre_ms",
		order=group_order,
		color="#4C78A8",
		width=0.5,
		showmeans=False,
		boxprops={"alpha": 0.9},
		medianprops={"color": "#111827", "linewidth": 2},
		whiskerprops={"color": "#374151", "linewidth": 1.5},
		capprops={"color": "#374151", "linewidth": 1.5},
		flierprops={"marker": "o", "markersize": 4, "markerfacecolor": "#9CA3AF", "markeredgecolor": "#9CA3AF", "alpha": 0.35},
		ax=ax,
	)

	ax.set_title(
		"Boxplot so sanh do tre (ms) giua Trong nuoc va Quoc te",
		fontsize=16,
		fontweight="bold",
		pad=14,
	)
	ax.set_xlabel("Loai may chu", fontsize=12)
	ax.set_ylabel("Do tre (ms)", fontsize=12)
	ax.set_xticks([0, 1])
	ax.set_xticklabels(["Trong nuoc", "Quoc te"], fontsize=11)
	ax.set_ylim(bottom=0)
	ax.grid(True, axis="y", alpha=0.25)
	ax.text(
		0.99,
		0.98,
		"\n".join(
			[
				f"Trong nuoc: n={int(group_stats.loc['Trong nuoc', 'count'])}, median={group_stats.loc['Trong nuoc', 'median']:.2f} ms, IQR={group_stats.loc['Trong nuoc', 'iqr']:.2f} ms",
				f"Quoc te: n={int(group_stats.loc['Quoc te', 'count'])}, median={group_stats.loc['Quoc te', 'median']:.2f} ms, IQR={group_stats.loc['Quoc te', 'iqr']:.2f} ms",
			]
		),
		transform=ax.transAxes,
		ha="right",
		va="top",
		fontsize=10,
		bbox={"facecolor": "white", "alpha": 0.95, "edgecolor": "#D1D5DB"},
	)

	fig.tight_layout()
	fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
	plt.close(fig)


def main() -> None:
	df = load_data()
	plot_boxplot(df)
	print(f"Da luu bieu do tai: {OUTPUT_FILE}")


if __name__ == "__main__":
	main()