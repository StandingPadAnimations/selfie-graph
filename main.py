# Copyright (C) 2026 Maryam Sheikh (Mahid Sheikh) <mahid@standingpad.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
from dataclasses import dataclass

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

SELFIE_Y_AXIS = 100
CUMULATIVE_SCALE_FACTOR = 4

DATA = {
    "Date_Label": [
        "2019-10",
        "2019-11",
        "2019-12",
        "2020-02",
        "2020-03",
        "2020-05",
        "2020-12",
        "2021-08",
        "2021-09",
        "2021-12",
        "2022-02",
        "2022-03",
        "2022-05",
        "2022-06",
        "2022-07",
        "2022-08",
        "2022-09",
        "2022-10",
        "2022-11",
        "2022-12",
        "2023-01",
        "2023-05",
        "2023-06",
        "2023-08",
        "2023-09",
        "2023-10",
        "2023-11",
        "2024-07",
        "2025-02",
        "2025-05",
        "2025-09",
        "2025-10",
        "2025-11",
        "2025-12",
        "2026-01",
        "2026-02",
        "2026-03",
        "2026-04",
        "2026-05",
        "2026-06",
        "2026-07"
    ],
    "Selfies": [
        5,
        2,
        4,
        2,
        3,
        1,
        4,
        3,
        2,
        2,
        1,
        2,
        2,
        3,
        2,
        11,
        1,
        3,
        4,
        1,
        1,
        1,
        1,
        1,
        8,
        2,
        1,
        6,
        1,
        2,
        4,
        14,
        8,
        21,
        8,
        15,
        21,
        17,
        5,
        13,
        9
    ],
}


@dataclass
class CutOff:
    date: str
    label: str
    line_color: str = "#505050"
    text_color: str = "#505050"


CUTOFFS: dict[str, list[CutOff]] = {
    "transition": [
        CutOff("2025-09", "Egg Crack", "#3e8eab", "#F5A9B8"),
        CutOff("2026-02", "Social Transition", "#3e8eab", "#F5A9B8"),
        CutOff("2026-05", "HRT", "#3e8eab", "#F5A9B8"),
    ],
    "school": [
        CutOff("2019-08", "Start of Middle School"),
        CutOff("2021-08", "Start of High School"),
        CutOff(
            "2025-07", "Start of University"
        ),  # One month earlier to avoid clipping with transition timelines
    ],
    "event": [
        CutOff("2020-03", "COVID-19 Lockdowns"),
        CutOff("2021-01", "Biden Presidency"),
        CutOff("2025-01", "Trump Presidency"),
    ],
    "life": [
        CutOff("2021-11", "Transition to MKA"),
        CutOff("2023-05", "End of Time in Band"),
    ],
}


def main():
    parser = argparse.ArgumentParser()
    _ = parser.add_argument("--q-mean", action="store_true")
    _ = parser.add_argument("--sum-egg-crack", action="store_true")
    _ = parser.add_argument("--cutoffs", metavar="cutoff", nargs="+")
    args = parser.parse_args()

    df = pd.DataFrame(DATA)
    df["Timestamp"] = pd.to_datetime(df["Date_Label"], format="%Y-%m")
    df = df.sort_values("Timestamp")
    fig, ax = plt.subplots(figsize=(12, 6))

    x_numeric = mdates.date2num(df["Timestamp"])

    ax.bar(
        df["Timestamp"],
        df["Selfies"],
        width=22,
        color="#1f77b4",
        alpha=0.75,
        edgecolor="none",
        align="center",
        label=f"Monthly Count (0-{SELFIE_Y_AXIS})",
    )

    # Aggragate selfies
    y_cumulative = df["Selfies"].cumsum().values

    ax2 = ax.twinx()
    if args.q_mean:
        df_time_indexed = df.set_index("Timestamp").sort_index()
        df_monthly_filled = df_time_indexed.resample("MS").asfreq().fillna(0)
        df_quarterly_average = df_monthly_filled.resample("QE")["Selfies"].mean()

        x_quar_average = df_quarterly_average.index
        y_quar_average = df_quarterly_average.values

        ax2.plot(
            x_quar_average,
            y_quar_average,
            color="#ff0000",
            linewidth=2,
            linestyle="-",
            drawstyle="steps-post",
            label=f"Quarterly Average (0-{SELFIE_Y_AXIS})",
        )
        ax2.fill_between(
            x_quar_average, y_quar_average, step="post", color="#ff0000", alpha=0.05
        )

    ax2.plot(
        x_numeric,
        y_cumulative,
        color="#2ca02c",
        linewidth=2,
        linestyle="-",
        drawstyle="steps-post",
        label=f"All-Time Cumulative Total (0-{SELFIE_Y_AXIS*CUMULATIVE_SCALE_FACTOR})",
    )
    ax2.fill_between(x_numeric, y_cumulative, step="post", color="#2ca02c", alpha=0.05)

    if args.sum_egg_crack:
        egg_crack_date = pd.to_datetime(CUTOFFS["transition"][0].date, format="%Y-%m")
        before_mask = df["Timestamp"] <= egg_crack_date
        after_mask = df["Timestamp"] >= egg_crack_date
        df_before = df[before_mask].copy()
        df_after = df[after_mask].copy()
        y_cum_before = df_before["Selfies"].cumsum().values
        y_cum_after = df_after["Selfies"].cumsum().values
        x_after = x_numeric[after_mask]

        pre_egg_crack_total = y_cum_before[-1] if len(y_cum_before) > 0 else 0

        ax2.hlines(
            y=pre_egg_crack_total,
            xmin=mdates.date2num(egg_crack_date),
            xmax=mdates.date2num(df["Timestamp"].iloc[-1]),
            color="#d62728",
            linewidth=2,
            linestyle=":",
            alpha=0.8,
            label=f"Cumulative Selfies at Egg Crack ({pre_egg_crack_total})",
        )

        ax2.plot(
            x_after,
            y_cum_after,
            color="#9467bd",
            linewidth=1.5,
            linestyle="-",
            drawstyle="steps-post",
            label=f"Cumulative From Egg Crack Forward (0-{SELFIE_Y_AXIS*CUMULATIVE_SCALE_FACTOR})",
        )
        ax2.fill_between(x_after, y_cum_after, step="post", color="#9467bd", alpha=0.15)

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=3))

    ax.set_ylim(0, SELFIE_Y_AXIS)
    ax2.set_ylim(0, SELFIE_Y_AXIS * CUMULATIVE_SCALE_FACTOR)

    def dynamic_y_pos(cutoff_date):
        historical_rows = df[df["Timestamp"] <= cutoff_date]
        current_total = (
            y_cumulative[len(historical_rows) - 1] if len(historical_rows) > 0 else 0
        )
        return (current_total / 400) * 100

    if args.cutoffs:
        cutoffs = []

        for option in args.cutoffs:
            if option in CUTOFFS:
                cutoffs += CUTOFFS[option]

        for cutoff in cutoffs:
            cutoff_date = pd.to_datetime(cutoff.date, format="%Y-%m")
            ax.axvline(
                x=cutoff_date,
                color=cutoff.line_color,
                linestyle="--",
                linewidth=1.5,
                alpha=0.5,
            )
            ax.text(
                x=cutoff_date + pd.DateOffset(days=5),
                y=dynamic_y_pos(cutoff_date) + 6,
                s=f"{cutoff.label}",
                color=cutoff.text_color,
                fontsize=10,
                fontweight="bold",
                rotation=90,
                horizontalalignment="left",
                verticalalignment="bottom",
                clip_on=False,
            )

    ax.set_ylabel(f"Selfies (0-{SELFIE_Y_AXIS})", color="#1f77b4")
    ax.tick_params(axis="y", labelcolor="#1f77b4")
    ax2.set_ylabel(f"Selfies (0-{SELFIE_Y_AXIS*CUMULATIVE_SCALE_FACTOR})", color="#2ca02c")
    ax2.tick_params(axis="y", labelcolor="#2ca02c")
    ax.set_xlabel("Year")
    ax.set_title("Selfies between 2019-2026")

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=True)

    ax.grid(True, which="major", linestyle="--", alpha=0.5)
    ax.grid(True, which="minor", linestyle=":", alpha=0.2)

    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig("monthly_counts_line_chart.svg")


if __name__ == "__main__":
    main()
