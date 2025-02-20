import streamlit as st
import pandas as pd
import os

# ファイルパス（データ保存用）
FILE_PATH = "data_store.csv"

# データを読み込む（空ファイルのヘッダー確認を追加）
def load_data():
    if os.path.exists(FILE_PATH) and os.path.getsize(FILE_PATH) > 0:
        df = pd.read_csv(FILE_PATH, dtype={"年-月": str})  # Ensure '年-月' is loaded as string
        # 確認: 必要なカラムがあるか
        required_columns = {"日付", "名前", "金額"}
        if not required_columns.issubset(df.columns):
            df = pd.DataFrame(columns=["日付", "名前", "金額"])
    else:
        df = pd.DataFrame(columns=["日付", "名前", "金額"])
    return df

# コーチ名簿（手動設定）
driver_list = ["平野", "ケイン", "山﨑", "萩原", "仙波し", "仙波ち", "久保田", "落合", "浜島", "野波",
               "末田", "芳本", "鈴木", "山田", "佐久間", "今井", "西川"]

# データを保存する（既存データと結合して保存）
def save_data(new_entries):
    df = load_data()  # Reload existing data
    df = pd.concat([df, new_entries], ignore_index=True)  # Append new data
    df["年-月"] = df["日付"].astype(str)  # Ensure '年-月' is always a string
    df.to_csv(FILE_PATH, index=False)  # Save back to file

# Streamlitアプリ
st.title("Fz車代管理アプリ")

# ナビゲーション
menu = st.sidebar.radio("メニュー", ["データ入力", "集計を表示", "CSVダウンロード"])

if menu == "データ入力":
    st.header("新しいデータを入力")
    date = st.date_input("日付を選択")
    selected_drivers = st.multiselect("運転手を選択", driver_list)
    
    amount = st.radio("金額を選択", [100, 300, 500])
    
    if st.button("送信"):
        new_entries = pd.DataFrame([[date, driver, amount] for driver in selected_drivers], columns=["日付", "名前", "金額"])
        save_data(new_entries)  # Save without overwriting old data
        st.success("データが追加されました！")
        st.rerun()  # Force app to refresh and reload new data

elif menu == "集計を表示":
    st.header("月ごとの集計")
    df = load_data()  # Ensure latest data is loaded
    if df.empty:
        st.warning("データがありません。")
    else:
        df["日付"] = pd.to_datetime(df["日付"], errors='coerce')
        df.dropna(subset=["日付"], inplace=True)
        df["年-月"] = df["日付"].dt.strftime("%Y-%m")  # Store as YYYY-MM string
        df["年-月"] = df["年-月"].astype(object)  # Ensure object type before display
        summary = df.groupby(["年-月", "名前"], as_index=False)["金額"].sum()
        all_names_df = pd.DataFrame({"名前": driver_list})
        summary = all_names_df.merge(summary, on="名前", how="left").fillna(0)
        summary["年-月"] = summary["年-月"].astype(str)  # Ensure string before displaying
        st.write(summary.pivot(index="年-月", columns="名前", values="金額").fillna(0))

elif menu == "CSVダウンロード":
    st.header("データをCSVでダウンロード")
    df = load_data()  # Ensure latest data is loaded
    if df.empty:
        st.warning("データがありません。")
    else:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(label="CSVをダウンロード", data=csv, file_name="fz_data.csv", mime="text/csv")
