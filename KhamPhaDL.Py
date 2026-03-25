from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "TgianPhanHoi_latency.xlsx"
OUTPUT_FILE = BASE_DIR / "Bang_Thong_Ke_Tong_Hop.xlsx"


def format_vn_number(value: float, digits: int = 2) -> str:
	"""Dinh dang so theo kieu Viet Nam: phan ngan cach hang nghin bang dau cham, thap phan bang dau phay."""
	if pd.isna(value):
		return "-"
	formatted = f"{value:,.{digits}f}"
	return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def format_vn_percent(value: float, digits: int = 2) -> str:
	"""Dinh dang phan tram theo kieu Viet Nam."""
	if pd.isna(value):
		return "-"
	return f"{value:.{digits}f}%".replace(".", ",")


def load_data() -> pd.DataFrame:
	"""Doc du lieu Excel dau vao, kiem tra cot bat buoc va lam sach du lieu truoc khi thong ke."""
	if not INPUT_FILE.exists():
		raise FileNotFoundError(f"Khong tim thay file du lieu: {INPUT_FILE}")

	df = pd.read_excel(INPUT_FILE)
	required_columns = {"Do_tre_ms", "Kich_thuoc_KB", "Loai_may_chu"}
	missing_columns = required_columns.difference(df.columns)
	if missing_columns:
		raise ValueError(
			"Thieu cot can thiet trong file Excel: " + ", ".join(sorted(missing_columns))
		)

	df = df.copy()
	df["Do_tre_ms"] = pd.to_numeric(df["Do_tre_ms"], errors="coerce")
	df["Kich_thuoc_KB"] = pd.to_numeric(df["Kich_thuoc_KB"], errors="coerce")
	df["Loai_may_chu"] = df["Loai_may_chu"].astype(str).str.strip()
	df = df.dropna(subset=["Do_tre_ms", "Kich_thuoc_KB", "Loai_may_chu"])

	if df.empty:
		raise ValueError("Khong co du lieu hop le de thong ke.")

	return df


def build_overall_summary(df: pd.DataFrame) -> pd.DataFrame:
	"""Tao bang thong ke tong quan cho cac cot so chinh trong tap du lieu."""
	columns = ["Do_tre_ms", "Kich_thuoc_KB"]
	rows = []

	for column in columns:
		series = df[column]
		rows.append(
			{
				"Chi_tieu": column,
				"So_mau": int(series.count()),
				"Trung_binh": series.mean(),
				"Trung_vi": series.median(),
				"Phuong_sai": series.var(),
				"Do_lech_chuan": series.std(),
				"Min": series.min(),
				"Max": series.max(),
				"Q1": series.quantile(0.25),
				"Q3": series.quantile(0.75),
				"CV (%)": (series.std() / series.mean()) * 100,
				"Skewness": series.skew(),
				"Kurtosis": series.kurt(),
			}
		)

	return pd.DataFrame(rows)[
		["Chi_tieu", "So_mau", "Trung_binh", "Trung_vi", "Do_lech_chuan", "Phuong_sai", "Min", "Max", "Q1", "Q3", "CV (%)", "Skewness", "Kurtosis"]
	]


def build_group_summary(df: pd.DataFrame) -> pd.DataFrame:
	"""Tao bang thong ke theo tung may chu de so sanh giua cac nhom du lieu."""
	rows = []
	for server_name, group in df.groupby("May_chu", sort=False):
		latency = group["Do_tre_ms"]
		rows.append(
			{
				"May_chu": server_name,
				"Loai": group["Loai_may_chu"].iloc[0],
				"N": int(latency.count()),
				"Trung_binh (ms)": latency.mean(),
				"Trung_vi (ms)": latency.median(),
				"Do_lech_chuan": latency.std(),
				"Min": latency.min(),
				"Max": latency.max(),
				"Skewness": latency.skew(),
			}
		)

	return pd.DataFrame(rows)[["May_chu", "Loai", "N", "Trung_binh (ms)", "Trung_vi (ms)", "Do_lech_chuan", "Min", "Max", "Skewness"]]


def build_compare_summary(df: pd.DataFrame) -> pd.DataFrame:
	"""Tao bang so sanh cac chi so giua nhom may chu quoc te va trong nuoc."""
	groups = ["Quoc te", "Trong nuoc"]
	group_series = {
		group_name: df.loc[df["Loai_may_chu"] == group_name, "Do_tre_ms"]
		for group_name in groups
	}
	group_labels = {
		group_name: f"{group_name} (N={int(series.count())})"
		for group_name, series in group_series.items()
	}

	metrics = [
		("Trung_binh (ms)", lambda s: s.mean()),
		("Trung_vi (ms)", lambda s: s.median()),
		("Do_lech_chuan", lambda s: s.std()),
		("CV (%)", lambda s: (s.std() / s.mean()) * 100),
		("Min (ms)", lambda s: s.min()),
		("Max (ms)", lambda s: s.max()),
		("Skewness", lambda s: s.skew()),
		("Kurtosis", lambda s: s.kurt()),
	]

	rows = []
	for metric_name, metric_func in metrics:
		row = {"Chi_tieu": metric_name}
		for group_name in groups:
			row[group_labels[group_name]] = metric_func(group_series[group_name])
		rows.append(row)

	return pd.DataFrame(rows)


def format_overall_for_print(df: pd.DataFrame) -> pd.DataFrame:
	"""Chuyen cac cot thong ke tong quan sang chuoi de in ra hoac xuat bao cao."""
	result = df.copy()
	for column in ["So_mau"]:
		result[column] = result[column].astype(int).astype(str)
	for column in ["Trung_binh", "Trung_vi", "Do_lech_chuan", "Phuong_sai", "Min", "Max", "Q1", "Q3", "Skewness", "Kurtosis"]:
		result[column] = result[column].map(lambda value: format_vn_number(value))
	result["CV (%)"] = result["CV (%)"].map(lambda value: format_vn_percent(value))
	return result


def format_group_for_print(df: pd.DataFrame) -> pd.DataFrame:
	"""Dinh dang bang thong ke theo nhom de hien thi gon va de doc hon."""
	result = df.copy()
	result["N"] = result["N"].astype(int).astype(str)
	for column in ["Trung_binh (ms)", "Trung_vi (ms)", "Do_lech_chuan", "Min", "Max", "Skewness"]:
		result[column] = result[column].map(lambda value: format_vn_number(value))
	return result


def format_compare_for_print(df: pd.DataFrame) -> pd.DataFrame:
	"""Dinh dang bang so sanh cac nhom de cac gia tri so hien thi dong nhat."""
	result = df.copy()
	for column in result.columns:
		if column != "Chi_tieu":
			result[column] = result[column].map(lambda value: format_vn_number(value))
	return result


def main() -> None:
	"""Ham chinh: nap du lieu, tao cac bang thong ke va ghi ket qua ra file Excel."""
	df = load_data()
	overall_summary = build_overall_summary(df)
	group_summary = build_group_summary(df)
	compare_summary = build_compare_summary(df)

	output_file = OUTPUT_FILE
	try:
		with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
			overall_summary.to_excel(writer, sheet_name="Tong_hop", index=False)
			group_summary.to_excel(writer, sheet_name="Theo_may_chu", index=False)
			compare_summary.to_excel(writer, sheet_name="So_sanh_nhom", index=False)
	except PermissionError:
		output_file = BASE_DIR / "Bang_Thong_Ke_Tong_Hop_moi.xlsx"
		with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
			overall_summary.to_excel(writer, sheet_name="Tong_hop", index=False)
			group_summary.to_excel(writer, sheet_name="Theo_may_chu", index=False)
			compare_summary.to_excel(writer, sheet_name="So_sanh_nhom", index=False)

	print(f"Da luu bang thong ke tong hop tai: {output_file}")


if __name__ == "__main__":
	main()