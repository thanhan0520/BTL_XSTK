from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "TgianPhanHoi_latency.xlsx"
OUTPUT_FILE = BASE_DIR / "histogram_do_tre_ms.png"


def load_data() -> pd.Series:
	if not EXCEL_FILE.exists():
		raise FileNotFoundError(f"Khong tim thay file du lieu: {EXCEL_FILE}")

	df = pd.read_excel(EXCEL_FILE)

	target_column = None
	for column_name in ("Do_tre_ms", "Latency_ms"):
		if column_name in df.columns:
			target_column = column_name
			break

	if target_column is None:
		raise ValueError(
			"Khong tim thay cot phu hop. Can cot 'Do_tre_ms' hoac 'Latency_ms'."
		)

	values = pd.to_numeric(df[target_column], errors="coerce").dropna()
	if values.empty:
		raise ValueError(f"Cot {target_column} khong co du lieu hop le de ve bieu do.")

	return values


def plot_histogram(values: pd.Series) -> None:
	plt.style.use("seaborn-v0_8-whitegrid")
	sns.set_context("notebook")

	fig, ax = plt.subplots(figsize=(11, 7))

	sns.histplot(
		values,
		bins=12,
		stat="count",
		kde=True,
		color="#4C78A8",
		edgecolor="white",
		alpha=0.85,
		line_kws={"linewidth": 2.2, "color": "#111827"},
		ax=ax,
	)

	q1 = values.quantile(0.25)
	q3 = values.quantile(0.75)
	mean_value = values.mean()
	median_value = values.median()
	std_value = values.std()
	min_value = values.min()
	max_value = values.max()
	iqr_value = q3 - q1

	ax.axvline(
		mean_value,
		color="#E63946",
		linestyle="--",
		linewidth=2.5,
		label=f"Mean = {mean_value:.2f} ms",
	)
	ax.axvline(
		median_value,
		color="#10B981",
		linestyle=":",
		linewidth=2.5,
		label=f"Median = {median_value:.2f} ms",
	)

	ax.set_title(
		"Histogram + KDE: Phan bo do tre (ms)",
		fontsize=16,
		fontweight="bold",
		pad=14,
	)
	ax.set_xlabel("Do tre (ms)", fontsize=12)
	ax.set_ylabel("Tan suat (so mau)", fontsize=12)
	ax.text(
		0.99,
		0.98,
		"\n".join(
			[
				f"So mau: {len(values)}",
				f"Min = {min_value:.2f} ms | Max = {max_value:.2f} ms",
				f"Mean = {mean_value:.2f} ms | Median = {median_value:.2f} ms",
				f"Std = {std_value:.2f} ms | IQR = {iqr_value:.2f} ms",
			]
		),
		transform=ax.transAxes,
		horizontalalignment="right",
		verticalalignment="top",
		fontsize=10,
		bbox={"facecolor": "white", "alpha": 0.95, "edgecolor": "#D1D5DB"},
	)
	ax.legend(frameon=True, loc="best")
	ax.grid(True, axis="y", alpha=0.2)

	fig.tight_layout()
	fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
	plt.close(fig)


def main() -> None:
	values = load_data()
	plot_histogram(values)
	print(f"Da luu bieu do tai: {OUTPUT_FILE}")


if __name__ == "__main__":
	main()