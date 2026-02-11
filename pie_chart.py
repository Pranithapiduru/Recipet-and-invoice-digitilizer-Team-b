import matplotlib.pyplot as plt


def spending_pie(df):
    if df.empty or df["total"].sum() == 0:
        return None

    fig, ax = plt.subplots()
    ax.pie(
        df["total"],
        labels=df["merchant"],
        autopct="%1.1f%%",
        startangle=90
    )
    ax.set_title("Spending by Merchant")

    return fig
