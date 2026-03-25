from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "DuLieu_ChiTiet_BTL.xlsx"
OUTPUT_FILE = BASE_DIR / "scatter_kich_thuoc_vs_do_tre.png"


def load_data() -> pd.DataFrame:
	if not EXCEL_FILE.exists():
		raise FileNotFoundError(f"Khong tim thay file du lieu: {EXCEL_FILE}")

	df = pd.read_excel(EXCEL_FILE)
	required_columns = {"Kich_thuoc_KB", "Do_tre_ms", "STT", "Dau_thoi_gian"}
	missing_columns = required_columns.difference(df.columns)
	if missing_columns:
		raise ValueError(
			"Thieu cot can thiet trong file Excel: " + ", ".join(sorted(missing_columns))
		)

	df = df[["STT", "Dau_thoi_gian", "Kich_thuoc_KB", "Do_tre_ms"]].copy()
	df["STT"] = pd.to_numeric(df["STT"], errors="coerce")
	df["Kich_thuoc_KB"] = pd.to_numeric(df["Kich_thuoc_KB"], errors="coerce")
	df["Do_tre_ms"] = pd.to_numeric(df["Do_tre_ms"], errors="coerce")
	df["Dau_thoi_gian"] = pd.to_datetime(df["Dau_thoi_gian"], errors="coerce")
	df = df.dropna(subset=["Kich_thuoc_KB", "Do_tre_ms", "STT", "Dau_thoi_gian"])

	if df.empty:
		raise ValueError("Khong co du lieu hop le de ve scatter plot.")

	return df


def plot_scatter(df: pd.DataFrame) -> None:
	plt.style.use("seaborn-v0_8-whitegrid")
	sns.set_context("notebook")

	fig, ax = plt.subplots(figsize=(11, 7))

	correlation = df["Kich_thuoc_KB"].corr(df["Do_tre_ms"])
	mean_x = df["Kich_thuoc_KB"].mean()
	mean_y = df["Do_tre_ms"].mean()
	std_x = df["Kich_thuoc_KB"].std()
	std_y = df["Do_tre_ms"].std()
	min_y = df["Do_tre_ms"].min()
	max_y = df["Do_tre_ms"].max()

	sns.regplot(
		data=df,
		x="Kich_thuoc_KB",
		y="Do_tre_ms",
		ax=ax,
		scatter_kws={
			"s": 40,
			"alpha": 0.6,
			"color": "#1D4ED8",
			"edgecolor": "none",
		},
		line_kws={"color": "#111827", "linewidth": 2.2},
	)

	ax.set_title(
		"Scatter plot: Tuong quan giua Kich thuoc va Do tre",
		fontsize=16,
		fontweight="bold",
		pad=14,
	)
	ax.set_xlabel("Kich thuoc (KB)", fontsize=12)
	ax.set_ylabel("Do tre (ms)", fontsize=12)
	ax.text(
		0.99,
		0.98,
		"\n".join(
			[
				f"So mau: {len(df)}",
				f"Pearson r = {correlation:.3f}",
				f"Mean X = {mean_x:.2f} KB | Mean Y = {mean_y:.2f} ms",
				f"Std X = {std_x:.2f} KB | Std Y = {std_y:.2f} ms",
				f"Min Y = {min_y:.2f} ms | Max Y = {max_y:.2f} ms",
			]
		),
		transform=ax.transAxes,
		ha="right",
		va="top",
		fontsize=10,
		bbox={"facecolor": "white", "alpha": 0.95, "edgecolor": "#D1D5DB"},
	)
	ax.grid(True, alpha=0.2)

	fig.tight_layout()
	fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
	plt.close(fig)


def main() -> None:
	df = load_data()
	plot_scatter(df)
	print(f"Da luu bieu do tai: {OUTPUT_FILE}")


if __name__ == "__main__":
	main()
