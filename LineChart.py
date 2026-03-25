from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
EXCEL_FILE = BASE_DIR / "TgianPhanHoi_latency.xlsx"
OUTPUT_FILE = BASE_DIR / "linechart_xu_huong.png"


def load_data() -> pd.DataFrame:
	if not EXCEL_FILE.exists():
		raise FileNotFoundError(f"Khong tim thay file du lieu: {EXCEL_FILE}")

	df = pd.read_excel(EXCEL_FILE)

	required_columns = {"STT", "Dau_thoi_gian", "Do_tre_ms"}
	missing_columns = required_columns.difference(df.columns)
	if missing_columns:
		raise ValueError(
			"Thieu cot can thiet trong file Excel: " + ", ".join(sorted(missing_columns))
		)

	df = df[["STT", "Dau_thoi_gian", "Do_tre_ms"]].copy()
	df["STT"] = pd.to_numeric(df["STT"], errors="coerce")
	df["Do_tre_ms"] = pd.to_numeric(df["Do_tre_ms"], errors="coerce")
	df["Dau_thoi_gian"] = pd.to_datetime(df["Dau_thoi_gian"], errors="coerce")
	df = df.dropna(subset=["STT", "Do_tre_ms", "Dau_thoi_gian"]).sort_values("STT")

	if df.empty:
		raise ValueError("Khong co du lieu hop le de ve line chart.")

	return df


def plot_line_chart(df: pd.DataFrame) -> None:
	plt.style.use("seaborn-v0_8-whitegrid")
	plt.rcParams["axes.unicode_minus"] = False
	fig, ax = plt.subplots(figsize=(12, 7))

	ax.plot(
		df["STT"],
		df["Do_tre_ms"],
		color="#2563EB",
		linewidth=2.2,
		marker="o",
		markersize=4,
		label="Do tre (ms)",
	)

	rolling_mean = df["Do_tre_ms"].rolling(window=5, min_periods=1).mean()
	ax.plot(
		df["STT"],
		rolling_mean,
		color="#F97316",
		linewidth=2,
		linestyle="--",
		label="Trung binh truot 5 mau",
	)

	mean_value = df["Do_tre_ms"].mean()
	median_value = df["Do_tre_ms"].median()
	std_value = df["Do_tre_ms"].std()
	min_value = df["Do_tre_ms"].min()
	max_value = df["Do_tre_ms"].max()

	ax.set_title(
		"Line chart xu huong do tre theo STT va thoi gian",
		fontsize=16,
		fontweight="bold",
		pad=14,
	)
	ax.set_xlabel("STT / Thu tu mau", fontsize=12)
	ax.set_ylabel("Do tre (ms)", fontsize=12)
	ax.legend(frameon=True, loc="best")
	ax.grid(True, alpha=0.2)

	step = max(len(df) // 10, 1)
	selected = df.iloc[::step].copy()
	if selected.iloc[-1]["STT"] != df.iloc[-1]["STT"]:
		selected = pd.concat([selected, df.iloc[[-1]]])
	ax.set_xticks(selected["STT"])
	ax.set_xticklabels(
		[
			f"{int(stt)}\n{moment.strftime('%H:%M:%S')}"
			for stt, moment in zip(selected["STT"], selected["Dau_thoi_gian"])
		],
		rotation=0,
		fontsize=9,
	)

	ax.text(
		0.99,
		0.98,
		"\n".join(
			[
				f"So mau: {len(df)}",
				f"Min = {min_value:.2f} ms | Max = {max_value:.2f} ms",
				f"Mean = {mean_value:.2f} ms | Median = {median_value:.2f} ms",
				f"Std = {std_value:.2f} ms",
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
	plot_line_chart(df)
	print(f"Da luu bieu do tai: {OUTPUT_FILE}")


if __name__ == "__main__":
	main()
